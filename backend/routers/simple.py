"""
Упрощённый ввод для логиста:
  POST /api/enrich           — обогатить маршрут внешними данными
  GET  /api/indicative-rate  — индикативная ставка фрахта по коридору
  POST /api/simple-analyze   — полный анализ без CSV
"""
from fastapi import APIRouter, HTTPException
import math

from schemas.simple import EnrichRequest, EnrichResponse, SimpleAnalyzeRequest
from schemas.analysis import Weights
from services.weather import get_weather_risk
from services.risk import get_route_geo_risk
from services.rates import get_route_params, get_cargo_surcharge, _BASE_INSURANCE_RATE
from services.freight_rates import get_indicative_rate
from services.fx import convert_to_usd
from services.tco import calculate_tco, calculate_score
from db.database import (
    save_analysis,
    save_analysis_results,
    upsert_route,
    insert_route_rate,
)

router = APIRouter()


async def _enrich_route(origin: str, destination: str, mode: str) -> dict:
    """Собирает все внешние параметры для одного маршрута."""
    route_p = get_route_params(origin, destination, mode)
    weather = await get_weather_risk(origin, destination)
    geo     = await get_route_geo_risk(origin, destination)

    return {
        "distance_km":              route_p["distance_km"],
        "transit_days":             route_p["base_transit_days"],
        "geo_risk":                 geo["geopolitical_risk_index"],
        "weather_risk":             weather["weather_risk_index"],
        "congestion":               route_p["congestion_index"],
        "emission_factor":          route_p["emission_factor_co2e_g_per_tkm"],
        "border_crossings":         route_p["border_crossings"],
        "port_calls":               route_p["port_calls"],
        "gauge_changes":            route_p["rail_gauge_change_count"],
        "customs_fee_per_border":   route_p["customs_fee_per_border_usd"],
        "handling_fee_per_port":    route_p["handling_fee_per_port_usd"],
        "carbon_price":             route_p["carbon_price_usd_per_ton"],
        "region_from":              route_p["region_from"],
        "region_to":                route_p["region_to"],
        "weather_details":          weather.get("details", []),
        "geo_details":              geo,
    }


@router.post("/enrich", response_model=EnrichResponse)
async def enrich(req: EnrichRequest):
    """
    Принимает: origin, destination, mode
    Возвращает: все параметры маршрута (погода, геополитика, расстояние, транзит, сборы, emissions)
    """
    try:
        data = await _enrich_route(req.origin, req.destination, req.mode)
    except Exception as e:
        raise HTTPException(500, f"Ошибка обогащения маршрута: {e}")

    return EnrichResponse(
        origin=req.origin,
        destination=req.destination,
        mode=req.mode,
        distance_km=data["distance_km"],
        transit_days=data["transit_days"],
        geo_risk=data["geo_risk"],
        weather_risk=data["weather_risk"],
        congestion=data["congestion"],
        emission_factor=data["emission_factor"],
        border_crossings=data["border_crossings"],
        port_calls=data["port_calls"],
        gauge_changes=data["gauge_changes"],
        customs_fee_per_border=data["customs_fee_per_border"],
        handling_fee_per_port=data["handling_fee_per_port"],
        carbon_price=data["carbon_price"],
        weather_details=data["weather_details"],
        geo_details=data["geo_details"],
    )


@router.get("/indicative-rate")
async def indicative_rate(
    origin: str,
    destination: str,
    mode: str,
    weight_tons: float = 1.0,
):
    """
    Возвращает индикативную ставку фрахта для коридора.
    Использует Freightos FBX (море) или ERAI (жд) если настроены API-ключи,
    иначе — публичные индикаторы Q1 2025.
    """
    try:
        route_p = get_route_params(origin, destination, mode)
        region_from = route_p["region_from"]
        region_to   = route_p["region_to"]

        rate_data = await get_indicative_rate(
            region_from, region_to, mode, weight_tons
        )
        return {
            "origin":      origin,
            "destination": destination,
            "mode":        mode,
            "region_from": region_from,
            "region_to":   region_to,
            **rate_data,
        }
    except Exception as e:
        raise HTTPException(500, f"Ошибка получения ставки: {e}")


@router.post("/simple-analyze")
async def simple_analyze(req: SimpleAnalyzeRequest):
    """
    Упрощённый анализ маршрутов — логист вводит только:
      - города, режим, ставку перевозчика (0 = автоматически взять индикативную)
      - параметры груза (вес, объём, стоимость, тип)
    Всё остальное рассчитывается автоматически.
    """
    if not req.routes:
        raise HTTPException(400, "Список маршрутов пуст")

    cargo     = req.cargo
    surcharge = get_cargo_surcharge(cargo.cargo_type)
    weights   = req.weights or Weights()
    w         = weights.model_dump()

    tco_data = []

    for route in req.routes:
        # 1. Получаем параметры коридора
        enriched = await _enrich_route(route.origin, route.destination, route.mode)

        # 1a. Апсертим маршрут в справочник routes
        route_code = f"{route.origin}-{route.destination}-{route.mode}".upper().replace(" ", "_")
        route_db_id = upsert_route(
            route_code=route_code,
            mode=route.mode,
            origin=route.origin,
            destination=route.destination,
            distance_km=enriched["distance_km"],
            transit_days_base=enriched["transit_days"],
            border_crossings=enriched["border_crossings"],
            port_calls=enriched["port_calls"],
            gauge_change_count=enriched["gauge_changes"],
        )

        # 2. Определяем базовую ставку фрахта
        if route.carrier_rate_usd and route.carrier_rate_usd > 0:
            # Логист ввёл ставку вручную — конвертируем в USD
            fx = await convert_to_usd(route.carrier_rate_usd, route.currency)
            base_cost_usd    = fx["usd"]
            rate_source      = f"Введено вручную ({route.currency})"
            rate_is_indicative = False
        else:
            # Ставка не введена — берём индикативную
            rate_data = await get_indicative_rate(
                enriched["region_from"], enriched["region_to"],
                route.mode, cargo.weight_tons
            )
            teu_count        = max(1, math.ceil(cargo.weight_tons / 20.0))
            base_cost_usd    = rate_data["rate_usd"] * teu_count
            rate_source      = rate_data["source"]
            rate_is_indicative = not rate_data["is_live"]
            fx = {"rate": 1.0, "original": base_cost_usd, "currency": "USD"}

        # 3. Применяем надбавки по типу груза
        insurance_rate = _BASE_INSURANCE_RATE * surcharge["insurance_mult"]
        handling_fee   = enriched["handling_fee_per_port"] * surcharge["handling_mult"]

        # 4. Собираем строку для calculate_tco
        row = {
            "route_id":                     route.route_id,
            "mode":                         route.mode,
            "origin":                       route.origin,
            "destination":                  route.destination,
            "base_cost_usd":                base_cost_usd,
            "base_transit_days":            enriched["transit_days"],
            "cargo_weight_tons":            cargo.weight_tons,
            "distance_km":                  enriched["distance_km"],
            "border_crossings":             enriched["border_crossings"],
            "port_calls":                   enriched["port_calls"],
            "rail_gauge_change_count":      enriched["gauge_changes"],
            "geopolitical_risk_index":      enriched["geo_risk"],
            "weather_risk_index":           enriched["weather_risk"],
            "congestion_index":             enriched["congestion"],
            "emission_factor_co2e_g_per_tkm": enriched["emission_factor"],
            "insurance_rate":               insurance_rate,
            "customs_fee_per_border_usd":   enriched["customs_fee_per_border"],
            "handling_fee_per_port_usd":    handling_fee,
            "carbon_price_usd_per_ton":     enriched["carbon_price"],
            "currency_fx_rate":             fx["rate"],
        }

        # Фиксируем ставку в route_rates (история ставок)
        try:
            insert_route_rate(
                route_id=route_db_id,
                rate_usd=base_cost_usd,
                source=rate_source,
                unit="per_shipment",
                raw={"is_indicative": rate_is_indicative, "currency": fx.get("currency", "USD")},
            )
        except Exception:
            pass  # запись истории не должна валить анализ

        tco_result = calculate_tco(row, cargo.cargo_value, cargo.capital_rate)
        tco_data.append({
            **row,
            **tco_result,
            "_route_db_id":       route_db_id,
            "_enriched":          enriched,
            "_fx":                fx,
            "_rate_source":       rate_source,
            "_rate_is_indicative": rate_is_indicative,
        })

    # 5. Скоринг
    all_tcos      = [r["total"]        for r in tco_data]
    all_days      = [r["transit_days"] for r in tco_data]
    all_risks     = [r["risk_index"]   for r in tco_data]
    all_emissions = [r["emissions"]    for r in tco_data]

    results = []
    for r in tco_data:
        score = calculate_score(
            r["total"], r["transit_days"], r["risk_index"], r["emissions"],
            w, all_tcos, all_days, all_risks, all_emissions,
        )
        results.append({
            "route_id":    r["_route_db_id"],
            "route_code":  r["route_id"],
            "mode":        r["mode"],
            "origin":      r["origin"],
            "destination": r["destination"],
            "cost_usd":    r["total"],
            "time_days":   r["transit_days"],
            "risk_index":  r["risk_index"],
            "emissions":   r["emissions"],
            "score":       score,
            "breakdown": {
                "base":        r["base_cost"],
                "customs":     r["customs"],
                "handling":    r["handling"],
                "carbon":      r["carbon"],
                "insurance":   r["insurance"],
                "working_cap": r["working_cap"],
                "inventory":   r["inventory"],
                "admin":       r["admin"],
                "contingency": r["contingency"],
            },
            "meta": {
                "distance_km":        r["_enriched"]["distance_km"],
                "geo_risk":           r["_enriched"]["geo_risk"],
                "weather_risk":       r["_enriched"]["weather_risk"],
                "carrier_rate":       r["_fx"]["original"],
                "currency":           r["_fx"]["currency"],
                "fx_rate":            r["_fx"]["rate"],
                "cargo_type":         cargo.cargo_type,
                "cargo_surcharge":    surcharge["label"],
                "rate_source":        r["_rate_source"],
                "rate_is_indicative": r["_rate_is_indicative"],
                "carbon_price_usd":   r["_enriched"]["carbon_price"],
                "region_from":        r["_enriched"]["region_from"],
                "region_to":          r["_enriched"]["region_to"],
            },
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    analysis_id = save_analysis(results, w, cargo.cargo_value, cargo.capital_rate)
    save_analysis_results(analysis_id, results)

    return {
        "id":           analysis_id,
        "results":      results,
        "weights":      w,
        "cargo_value":  cargo.cargo_value,
        "capital_rate": cargo.capital_rate,
        "cargo_type":   cargo.cargo_type,
    }
