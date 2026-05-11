"""
Геометрия маршрутов: POST /api/route_geometry, GET /api/route-geometry

Море — searoute-py (огибание континентов, проливы, каналы).
Ж/Д   — OSRM (router.project-osrm.org) по реальной дорожной сети
        вдоль предзаданных евразийских коридоров. Fallback — waypoints.
"""
import httpx
from fastapi import APIRouter, HTTPException

from schemas.routes import RouteGeomRequest
from services.geocoding import (
    get_coords, sea_waypoints, rail_waypoints,
    _interp, _CORRIDORS,
)

router = APIRouter()

OSRM_BASE = "https://router.project-osrm.org"
_OSRM_TIMEOUT = 8.0


def _try_searoute(from_c, to_c):
    """Морской маршрут через searoute-py. Возвращает (pts, source) или (None, reason)."""
    try:
        import searoute as sr
        route = sr.searoute(
            [from_c[1], from_c[0]],   # searoute ожидает [lon, lat]
            [to_c[1],   to_c[0]],
            units="km",
        )
        if route and route.get("geometry"):
            coords = route["geometry"]["coordinates"]
            pts = [[lat, lon] for lon, lat in coords]
            return pts, "searoute"
    except Exception as e:
        return None, f"searoute_error:{str(e)[:80]}"
    return None, "searoute_empty"


def _pick_corridor(from_lat, from_lon, to_lat, to_lon):
    """Возвращает выбранный коридор (список waypoint'ов) для пары точек, либо None."""
    def inChina(la, lo):    return 98 < lo < 135 and 18 < la < 55
    def inRussia(la, lo):   return 28 < lo < 145 and 48 < la < 75
    def inEurope(la, lo):   return -5 < lo < 35  and 36 < la < 62
    def inCentAsia(la, lo): return 55 < lo < 90  and 36 < la < 55
    def inFarEast(la, lo):  return lo > 128       and 35 < la < 55
    def inKorea(la, lo):    return 126 < lo < 130 and 34 < la < 39

    if (inChina(from_lat, from_lon) or inFarEast(from_lat, from_lon)) and \
       (inEurope(to_lat, to_lon) or (inRussia(to_lat, to_lon) and to_lon < 60)):
        return _CORRIDORS["china_eu"]
    if (inEurope(from_lat, from_lon) or (inRussia(from_lat, from_lon) and from_lon < 60)) and \
       (inChina(to_lat, to_lon) or inFarEast(to_lat, to_lon)):
        return list(reversed(_CORRIDORS["china_eu"]))
    if inKorea(from_lat, from_lon) and inEurope(to_lat, to_lon):
        return _CORRIDORS["korea_eu"]
    if inEurope(from_lat, from_lon) and inKorea(to_lat, to_lon):
        return list(reversed(_CORRIDORS["korea_eu"]))
    if inRussia(from_lat, from_lon) and inFarEast(to_lat, to_lon):
        return _CORRIDORS["transsib"]
    if inFarEast(from_lat, from_lon) and inRussia(to_lat, to_lon):
        return list(reversed(_CORRIDORS["transsib"]))
    if inRussia(from_lat, from_lon) and inEurope(to_lat, to_lon):
        return _CORRIDORS["ru_eu"]
    if inEurope(from_lat, from_lon) and inRussia(to_lat, to_lon):
        return list(reversed(_CORRIDORS["ru_eu"]))
    if inChina(from_lat, from_lon) and inRussia(to_lat, to_lon):
        return _CORRIDORS["china_ru"]
    if inCentAsia(from_lat, from_lon) or inCentAsia(to_lat, to_lon):
        return _CORRIDORS["centasia_eu"]
    return None


def _osrm_segment(client: httpx.Client, a: tuple, b: tuple) -> list | None:
    """Запрашивает у OSRM маршрут между двумя точками. Возвращает [[lat, lon], ...] либо None."""
    url = f"{OSRM_BASE}/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}"
    try:
        r = client.get(url, params={"overview": "full", "geometries": "geojson"})
        if r.status_code != 200:
            return None
        data = r.json()
        if data.get("code") != "Ok" or not data.get("routes"):
            return None
        coords = data["routes"][0]["geometry"]["coordinates"]
        return [[c[1], c[0]] for c in coords]
    except Exception:
        return None


def _try_osrm_rail(from_lat, from_lon, to_lat, to_lon) -> tuple[list | None, str]:
    """
    Строит ж/д маршрут через OSRM по реальной дорожной сети, идущей вдоль жд-коридоров.

    Логика: подбираем коридор → берём ближайшие узлы входа/выхода → запрашиваем у OSRM
    путь из (origin → entry_node → промежуточные узлы → exit_node → destination).
    OSRM driving-routes по сети дорог в Евразии в большинстве участков почти повторяют
    полотно Транссиба / China-Europe / Шёлкового пути.
    """
    corridor = _pick_corridor(from_lat, from_lon, to_lat, to_lon)
    if corridor is None:
        chain = [(from_lat, from_lon), (to_lat, to_lon)]
    else:
        def d2(p, q): return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
        fi = min(range(len(corridor)), key=lambda i: d2((from_lat, from_lon), corridor[i]))
        ti = min(range(len(corridor)), key=lambda i: d2((to_lat, to_lon), corridor[i]))
        slc = corridor[fi:ti + 1] if fi <= ti else list(reversed(corridor[ti:fi + 1]))
        chain = [(from_lat, from_lon)] + list(slc) + [(to_lat, to_lon)]

    if len(chain) < 2:
        return None, "no_chain"

    # OSRM поддерживает многоточечные маршруты; шлём всё одним запросом для скорости.
    coords_str = ";".join(f"{p[1]},{p[0]}" for p in chain)
    url = f"{OSRM_BASE}/route/v1/driving/{coords_str}"
    try:
        with httpx.Client(timeout=_OSRM_TIMEOUT) as client:
            r = client.get(url, params={"overview": "full", "geometries": "geojson"})
            if r.status_code != 200:
                return None, f"osrm_http_{r.status_code}"
            data = r.json()
            if data.get("code") != "Ok" or not data.get("routes"):
                return None, f"osrm_code_{data.get('code')}"
            coords = data["routes"][0]["geometry"]["coordinates"]
            return [[c[1], c[0]] for c in coords], "osrm"
    except Exception as e:
        return None, f"osrm_error:{str(e)[:60]}"


@router.post("/route_geometry")
def route_geometry_post(req: RouteGeomRequest):
    """Возвращает GeoJSON-координаты маршрута (sea/rail)."""
    from_c = get_coords(req.origin)
    to_c   = get_coords(req.destination)

    if not from_c:
        raise HTTPException(400, f"Координаты не найдены: {req.origin}")
    if not to_c:
        raise HTTPException(400, f"Координаты не найдены: {req.destination}")

    mode   = req.mode.lower()
    result = {"origin_coords": list(from_c), "destination_coords": list(to_c)}

    sea_pts, sea_src = _try_searoute(from_c, to_c)
    if not sea_pts:
        sea_pts = sea_waypoints(from_c[0], from_c[1], to_c[0], to_c[1])
        sea_src = "waypoints"

    rail_pts, rail_src = _try_osrm_rail(from_c[0], from_c[1], to_c[0], to_c[1])
    if not rail_pts:
        rail_pts = rail_waypoints(from_c[0], from_c[1], to_c[0], to_c[1])
        rail_src = "waypoints"

    result["sea"]         = sea_pts
    result["sea_source"]  = sea_src
    result["rail"]        = rail_pts
    result["rail_source"] = rail_src
    return result


@router.get("/route-geometry")
def route_geometry_get(
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float,
    mode: str = "sea",
):
    """Координаты маршрута (sea/rail) для отрисовки на карте."""
    mode = mode.lower()

    if mode == "sea":
        pts, src = _try_searoute((from_lat, from_lon), (to_lat, to_lon))
        if not pts:
            pts = sea_waypoints(from_lat, from_lon, to_lat, to_lon)
            pts = [[p[0], p[1]] for p in pts]
            src = "waypoints"
        return {"source": src, "coordinates": pts}

    if mode == "rail":
        pts, src = _try_osrm_rail(from_lat, from_lon, to_lat, to_lon)
        if not pts:
            pts = rail_waypoints(from_lat, from_lon, to_lat, to_lon)
            pts = [[p[0], p[1]] for p in pts]
            src = "waypoints"
        return {"source": src, "coordinates": pts}

    pts = _interp([(from_lat, from_lon), (to_lat, to_lon)], 40)
    return {"source": "straight", "coordinates": [[p[0], p[1]] for p in pts]}
