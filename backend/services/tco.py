"""
Сервис расчёта TCO (Total Cost of Ownership) и скоринга маршрутов
"""


def calculate_tco(row: dict, cargo_value: float, capital_rate: float) -> dict:
    """Рассчитывает полную стоимость владения для одного маршрута."""
    base_cost    = float(row.get("base_cost_usd", 0))
    transit_days = float(row.get("base_transit_days", 0))
    weight       = float(row.get("cargo_weight_tons", 1))
    borders      = float(row.get("border_crossings", 0))
    ports        = float(row.get("port_calls", 0))
    geo_risk     = float(row.get("geopolitical_risk_index", 0))
    weather_risk = float(row.get("weather_risk_index", 0))
    congestion   = float(row.get("congestion_index", 0))
    gauge_change = float(row.get("rail_gauge_change_count", 0))
    ef           = float(row.get("emission_factor_co2e_g_per_tkm", 0))
    distance     = float(row.get("distance_km", 0))
    # ИСПРАВЛЕНО (v2): дефолт был 0.02 (2%) — завышено в 10 раз.
    # Реальная ставка карго-страховки: 0.1–0.3%. Дефолт выравнен с _BASE_INSURANCE_RATE.
    insurance    = float(row.get("insurance_rate", 0.002))
    customs_fee  = float(row.get("customs_fee_per_border_usd", 0))
    handling_fee = float(row.get("handling_fee_per_port_usd", 0))
    carbon_price = float(row.get("carbon_price_usd_per_ton", 0))
    mode         = str(row.get("mode", "sea")).lower()

    risk_index = round(min(1.0, geo_risk * 0.5 + weather_risk * 0.3 + congestion * 0.2), 3)

    emissions   = round((ef * distance * weight) / 1_000_000, 3)
    carbon_cost = round(emissions * carbon_price, 2)

    customs_total  = borders * customs_fee
    handling_total = ports * handling_fee
    gauge_cost     = gauge_change * 200

    prepay_rate    = 0.30 if mode == "sea" else 0.15
    pretransit_cap = base_cost * prepay_rate * (capital_rate / 100) * (transit_days / 365)
    # ИСПРАВЛЕНО (v2): ранее intransit_cap считался от полного cargo_value,
    # создавая двойной счёт с pretransit_cap (аванс уже включён в замороженный капитал).
    # Теперь вычитаем уже учтённый авансовый платёж перевозчику.
    prepaid_amount = base_cost * prepay_rate
    intransit_cap  = (cargo_value - prepaid_amount) * (capital_rate / 100) * (transit_days / 365)
    inventory_cost = cargo_value * 0.002 * max(0, transit_days - 5) / 30

    insurance_cost = cargo_value * insurance
    admin_cost     = base_cost * 0.02
    contingency    = base_cost * risk_index * 0.15

    total = round(
        base_cost + customs_total + handling_total + gauge_cost +
        carbon_cost + pretransit_cap + intransit_cap + inventory_cost +
        insurance_cost + admin_cost + contingency,
        2,
    )

    return {
        "base_cost":    round(base_cost, 2),
        "customs":      round(customs_total, 2),
        "handling":     round(handling_total, 2),
        "carbon":       round(carbon_cost, 2),
        "insurance":    round(insurance_cost, 2),
        "working_cap":  round(pretransit_cap + intransit_cap, 2),
        "inventory":    round(inventory_cost, 2),
        "admin":        round(admin_cost, 2),
        "contingency":  round(contingency, 2),
        "total":        total,
        "risk_index":   risk_index,
        "emissions":    emissions,
        "transit_days": int(transit_days),
    }


def calculate_score(
    tco: float,
    transit_days: int,
    risk_index: float,
    emissions: float,
    weights: dict,
    all_tcos: list,
    all_days: list,
    all_risks: list,
    all_emissions: list,
) -> float:
    """Нормализованный балл маршрута (чем выше — тем лучше)."""

    def norm_lower_better(val, vals):
        mn, mx = min(vals), max(vals)
        if mx == mn:
            return 0.5
        return round(1.0 - (val - mn) / (mx - mn), 6)

    s_cost = norm_lower_better(tco,          all_tcos)
    s_time = norm_lower_better(transit_days, all_days)
    s_risk = norm_lower_better(risk_index,   all_risks)
    s_emis = norm_lower_better(emissions,    all_emissions)

    total_w = weights["cost"] + weights["time"] + weights["risk"] + weights["emissions"]
    if total_w == 0:
        return 0.0

    score = (
        s_cost * weights["cost"] +
        s_time * weights["time"] +
        s_risk * weights["risk"] +
        s_emis * weights["emissions"]
    ) / total_w

    if risk_index > 0.8:    score *= 0.70
    elif risk_index > 0.6:  score *= 0.85
    if transit_days > 90:   score *= 0.85
    elif transit_days > 60: score *= 0.92

    return round(min(score, 1.0), 4)
