"""
Погодный риск маршрута через Open-Meteo API (бесплатно, без ключа).
Берём несколько промежуточных точек вдоль маршрута и оцениваем риск
по осадкам, скорости ветра и коду погоды.
"""
import httpx
from services.geocoding import get_coords, _interp

_SAMPLE_POINTS = 5
_TIMEOUT = 8.0


async def get_weather_risk(origin: str, destination: str) -> dict:
    """
    Возвращает weather_risk_index [0..1] и детали по точкам маршрута.
    Если API недоступен — возвращает нейтральное значение 0.3.
    """
    from_c = get_coords(origin)
    to_c   = get_coords(destination)

    if not from_c or not to_c:
        return {"weather_risk_index": 0.3, "source": "default", "details": []}

    pts  = _interp([from_c, to_c], _SAMPLE_POINTS * 2)
    step = max(1, len(pts) // _SAMPLE_POINTS)
    sample = pts[::step][:_SAMPLE_POINTS]

    risks   = []
    details = []

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        for lat, lon in sample:
            try:
                resp = await client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude":      round(lat, 4),
                        "longitude":     round(lon, 4),
                        "daily":         "precipitation_sum,windspeed_10m_max,weathercode",
                        "forecast_days": 3,
                        "timezone":      "auto",
                    },
                )
                if resp.status_code != 200:
                    risks.append(0.3)
                    continue

                data       = resp.json().get("daily", {})
                precip     = data.get("precipitation_sum", [0])
                wind       = data.get("windspeed_10m_max", [0])
                codes      = data.get("weathercode", [0])
                max_precip = max(precip) if precip else 0
                max_wind   = max(wind)   if wind   else 0
                max_code   = max(codes)  if codes  else 0

                r_precip    = min(1.0, max_precip / 50.0)
                r_wind      = min(1.0, max_wind   / 80.0)
                r_code      = 1.0 if max_code >= 70 else (0.5 if max_code >= 50 else 0.1)
                point_risk  = round(r_precip * 0.4 + r_wind * 0.4 + r_code * 0.2, 3)

                risks.append(point_risk)
                details.append({
                    "lat":       round(lat, 3),
                    "lon":       round(lon, 3),
                    "precip_mm": round(max_precip, 1),
                    "wind_kmh":  round(max_wind,   1),
                    "code":      max_code,
                    "risk":      point_risk,
                })

            except Exception as ex:
                risks.append(0.3)
                details.append({
                    "lat":   round(lat, 3),
                    "lon":   round(lon, 3),
                    "error": str(ex)[:80],
                    "risk":  0.3,
                })

    weather_risk = round(sum(risks) / len(risks), 3) if risks else 0.3
    source = "open-meteo" if any("precip_mm" in d for d in details) else "default"
    return {
        "weather_risk_index": weather_risk,
        "source":             source,
        "details":            details,
    }
