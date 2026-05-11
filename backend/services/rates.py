"""
Справочник параметров маршрутов: транзитные дни, emission factors,
таможенные сборы, congestion index по коридорам.
Базируется на данных IMO, IPCC, UNCTAD, публичных тарифах UTLC ERA.
"""
import math
from services.geocoding import get_coords

# ─── Emission factors (г CO2e / тонно-км) ────────────────────────────────────
# Источник: IMO 4th GHG Study 2020, IPCC AR6
EMISSION_FACTORS = {
    "sea":  8.0,   # контейнеровоз (среднее по флоту)
    "rail": 22.0,  # электрифицированная ж/д (среднее по Евразии)
    "road": 80.0,  # грузовик (для сравнения)
}

# ─── Скорости движения (км/сутки) ────────────────────────────────────────────
# ИСПРАВЛЕНО: ранее sea=22 трактовалось как «узлы» но делилось на 22*24 (528 км/сут).
# Теперь все значения явно в км/сутки для единообразия.
_SPEED_KPD = {
    "sea":   500,   # км/сутки с учётом стоянок в портах (~20.8 km/h eff.)
    "rail":  900,   # км/сутки по данным UTLC ERA
}

# ─── Надбавки по типу груза ───────────────────────────────────────────────────
CARGO_SURCHARGES = {
    "обычный":          {"insurance_mult": 1.0, "handling_mult": 1.0, "label": "Обычный"},
    "ordinary":         {"insurance_mult": 1.0, "handling_mult": 1.0, "label": "Обычный"},
    "опасный":          {"insurance_mult": 2.5, "handling_mult": 1.8, "label": "Опасный"},
    "dangerous":        {"insurance_mult": 2.5, "handling_mult": 1.8, "label": "Опасный"},
    "hazardous":        {"insurance_mult": 2.5, "handling_mult": 1.8, "label": "Опасный"},
    "скоропортящийся":  {"insurance_mult": 1.8, "handling_mult": 1.4, "label": "Скоропортящийся"},
    "perishable":       {"insurance_mult": 1.8, "handling_mult": 1.4, "label": "Скоропортящийся"},
    "refrigerated":     {"insurance_mult": 1.8, "handling_mult": 1.4, "label": "Скоропортящийся"},
}

# ─── Параметры по коридорам (borders, ports, gauge changes, congestion) ───────
# Ключ: (регион_отправки, регион_назначения, mode)
_CORRIDOR_PARAMS = {
    # Китай ↔ Европа
    ("china", "europe", "sea"):  {"borders": 0, "ports": 2, "gauge": 0, "congestion": 0.35, "days_base": 28},
    ("china", "europe", "rail"): {"borders": 4, "ports": 0, "gauge": 1, "congestion": 0.25, "days_base": 14},
    # Китай ↔ Россия
    ("china", "russia", "sea"):  {"borders": 0, "ports": 2, "gauge": 0, "congestion": 0.30, "days_base": 12},
    ("china", "russia", "rail"): {"borders": 2, "ports": 0, "gauge": 1, "congestion": 0.30, "days_base": 8},
    # Россия ↔ Европа
    ("russia", "europe", "sea"):  {"borders": 0, "ports": 2, "gauge": 0, "congestion": 0.40, "days_base": 10},
    ("russia", "europe", "rail"): {"borders": 3, "ports": 0, "gauge": 1, "congestion": 0.35, "days_base": 7},
    # Корея/Япония ↔ Европа
    ("korea", "europe", "sea"):  {"borders": 0, "ports": 2, "gauge": 0, "congestion": 0.35, "days_base": 30},
    ("korea", "europe", "rail"): {"borders": 5, "ports": 0, "gauge": 1, "congestion": 0.28, "days_base": 18},
    # Центральная Азия ↔ Европа
    ("central_asia", "europe", "rail"): {"borders": 4, "ports": 0, "gauge": 1, "congestion": 0.30, "days_base": 12},
    # Ближний Восток ↔ Европа
    ("middle_east", "europe", "sea"):  {"borders": 0, "ports": 2, "gauge": 0, "congestion": 0.45, "days_base": 14},
    # Китай ↔ США
    ("china", "north_america", "sea"): {"borders": 0, "ports": 2, "gauge": 0, "congestion": 0.50, "days_base": 18},
}

# ─── Таможенные сборы по регионам (USD за пересечение) ───────────────────────
_CUSTOMS_FEE_BY_REGION = {
    "europe":       350,
    "russia":       500,
    "china":        300,
    "central_asia": 400,
    "middle_east":  450,
    "korea":        280,
    "north_america": 200,
    "default":      400,
}

# ─── Сборы за обработку в портах/хабах (USD за остановку) ────────────────────
_HANDLING_FEE_BY_MODE = {
    "sea":  450,
    "rail": 200,
}

# ─── Базовая ставка страховки ─────────────────────────────────────────────────
# ИСПРАВЛЕНО: было 1.5% (0.015) — это грубая ошибка.
# Реальная ставка карго-страховки: 0.1–0.3% от стоимости груза.
# Источник: Lloyd's, международная практика ICC (A), Русское общество (СОГАЗ).
# При опасном грузе множитель из CARGO_SURCHARGES даёт 0.5–0.75% — это корректно.
_BASE_INSURANCE_RATE = 0.002  # 0.2% от стоимости груза

# ─── Цены на углерод по регионам (USD/т CO2e) ────────────────────────────────
# ИСПРАВЛЕНО: ранее 15 USD/т захардкожено для всех маршрутов.
# EU ETS: ~60–70 EUR/т (≈65 USD) в 2024–2025.
# Прочие регионы: ~10–20 USD/т (добровольные рынки / нет ETS).
# Источник: ICE, World Bank Carbon Pricing Dashboard 2024.
_CARBON_PRICE_BY_REGION = {
    "europe":        65.0,   # EU ETS, ~60–70 EUR/т
    "north_america": 20.0,   # CA cap-and-trade + добровольный рынок
    "china":         10.0,   # ETS Китай (ещё в развитии)
    "russia":        12.0,   # нет ETS, оценка добровольного рынка
    "korea":         15.0,   # K-ETS
    "central_asia":  10.0,   # нет ETS
    "middle_east":   10.0,   # нет ETS
    "default":       15.0,
}


def get_carbon_price(region_from: str, region_to: str) -> float:
    """Возвращает цену углерода: берём максимум между регионами маршрута."""
    p_from = _CARBON_PRICE_BY_REGION.get(region_from, _CARBON_PRICE_BY_REGION["default"])
    p_to   = _CARBON_PRICE_BY_REGION.get(region_to,   _CARBON_PRICE_BY_REGION["default"])
    return round(max(p_from, p_to), 2)


def _get_region(city: str) -> str:
    """Определяет регион по названию города."""
    from services.risk import _CITY_TO_COUNTRY
    key     = city.lower().strip()
    country = _CITY_TO_COUNTRY.get(key)
    if country:
        eu = {"Germany","Netherlands","Belgium","France","United Kingdom","Poland","Czechia",
              "Austria","Finland","Sweden","Norway","Denmark","Spain","Italy","Portugal",
              "Hungary","Romania","Bulgaria","Croatia","Estonia","Latvia","Lithuania",
              "Slovakia","Greece","Switzerland","Serbia","Bosnia-Herzegovina","Albania",
              "North Macedonia","Moldova","Slovenia","Luxembourg","Ireland"}
        ru = {"Russia"}
        cn = {"China"}
        kr = {"South Korea","Japan"}
        ca = {"Kazakhstan","Uzbekistan","Turkmenistan","Kyrgyzstan","Tajikistan"}
        me = {"United Arab Emirates","Saudi Arabia","Qatar","Kuwait","Oman","Bahrain",
              "Jordan","Lebanon","Israel","Turkey","Egypt","Iran","Iraq"}
        na = {"United States","Canada","Mexico"}
        if country in eu: return "europe"
        if country in ru: return "russia"
        if country in cn: return "china"
        if country in kr: return "korea"
        if country in ca: return "central_asia"
        if country in me: return "middle_east"
        if country in na: return "north_america"

    coords = get_coords(city)
    if coords:
        lat, lon = coords
        boxes = [
            ("europe",       (36, 71, -10, 40)),
            ("russia",       (48, 75,  40, 145)),
            ("china",        (18, 55,  90, 145)),
            ("korea",        (30, 45, 124, 145)),
            ("central_asia", (35, 55,  40,  90)),
            ("middle_east",  (12, 42,  25,  65)),
            ("north_america",(15, 72,-170, -52)),
        ]
        for region, (la1, la2, lo1, lo2) in boxes:
            if la1 <= lat <= la2 and lo1 <= lon <= lo2:
                return region

    return "default"


def _haversine(c1: tuple, c2: tuple) -> float:
    """Расстояние между двумя точками в км."""
    R = 6371
    lat1, lon1 = math.radians(c1[0]), math.radians(c1[1])
    lat2, lon2 = math.radians(c2[0]), math.radians(c2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return round(2 * R * math.asin(math.sqrt(a)), 1)


def get_route_params(origin: str, destination: str, mode: str) -> dict:
    """
    Возвращает параметры маршрута: расстояние, дни, сборы, emission factor,
    congestion и т.д. — всё что нужно для TCO кроме базовой ставки фрахта.
    """
    mode = mode.lower().strip()

    from_c = get_coords(origin)
    to_c   = get_coords(destination)

    # Расстояние
    distance_km = _haversine(from_c, to_c) if from_c and to_c else 5000.0
    # Для моря умножаем на коэффициент реального маршрута (огибает континенты)
    if mode == "sea":
        distance_km = round(distance_km * 1.35, 1)
    elif mode == "rail":
        distance_km = round(distance_km * 1.15, 1)

    # Регионы
    region_from = _get_region(origin)
    region_to   = _get_region(destination)

    # Ищем параметры коридора (пробуем оба направления)
    key_fwd = (region_from, region_to, mode)
    key_rev = (region_to, region_from, mode)
    corridor = (
        _CORRIDOR_PARAMS.get(key_fwd) or
        _CORRIDOR_PARAMS.get(key_rev) or
        # Дефолт по mode
        {"borders": 2, "ports": 1, "gauge": 0, "congestion": 0.30, "days_base": 0}
    )

    # ИСПРАВЛЕНО (v2): transit_days = max(days_base, days_dist), а не одно из двух.
    # Это гарантирует, что реальное расстояние всегда влияет на результат:
    # длинный маршрут никогда не получит меньше дней, чем требует физика.
    speed_kpd    = _SPEED_KPD.get(mode, 500)
    days_dist    = math.ceil(distance_km / speed_kpd)
    transit_days = max(1, corridor["days_base"], days_dist)

    emission_factor = EMISSION_FACTORS.get(mode, 30.0)

    # ИСПРАВЛЕНО (v2): customs_fee — средняя ставка по регионам маршрута,
    # а не только от региона отправки. Отражает реальные сборы всех юрисдикций.
    if corridor["borders"] > 0:
        fee_from    = _CUSTOMS_FEE_BY_REGION.get(region_from, _CUSTOMS_FEE_BY_REGION["default"])
        fee_to      = _CUSTOMS_FEE_BY_REGION.get(region_to,   _CUSTOMS_FEE_BY_REGION["default"])
        customs_fee = round((fee_from + fee_to) / 2)
    else:
        customs_fee = 0

    handling_fee = _HANDLING_FEE_BY_MODE.get(mode, 300)
    carbon_price = get_carbon_price(region_from, region_to)

    return {
        "distance_km":                  distance_km,
        "base_transit_days":            transit_days,
        "border_crossings":             corridor["borders"],
        "port_calls":                   corridor["ports"],
        "rail_gauge_change_count":      corridor["gauge"],
        "congestion_index":             corridor["congestion"],
        "emission_factor_co2e_g_per_tkm": emission_factor,
        "customs_fee_per_border_usd":   customs_fee,
        "handling_fee_per_port_usd":    handling_fee,
        "carbon_price_usd_per_ton":     carbon_price,
        "region_from":                  region_from,
        "region_to":                    region_to,
    }


def get_cargo_surcharge(cargo_type: str) -> dict:
    """Возвращает множители надбавок по типу груза."""
    key = cargo_type.lower().strip()
    return CARGO_SURCHARGES.get(key, CARGO_SURCHARGES["обычный"])


def apply_cargo_surcharges(base_insurance_rate: float, base_handling_fee: float,
                            cargo_type: str) -> tuple[float, float]:
    """Применяет надбавки по типу груза к страховке и handling."""
    surcharge = get_cargo_surcharge(cargo_type)
    return (
        round(base_insurance_rate * surcharge["insurance_mult"], 4),
        round(base_handling_fee   * surcharge["handling_mult"],  2),
    )
