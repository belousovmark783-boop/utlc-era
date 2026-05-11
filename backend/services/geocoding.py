"""
Геокодирование городов/портов и построение маршрутных геометрий
"""

# ─── Словарь координат ───────────────────────────────────────────────────────

CITY_COORDS: dict[str, tuple[float, float]] = {
    "москва": (55.7558, 37.6173), "moscow": (55.7558, 37.6173),
    "санкт-петербург": (59.9311, 30.3609), "saint petersburg": (59.9311, 30.3609), "spb": (59.9311, 30.3609), "питер": (59.9311, 30.3609),
    "новосибирск": (54.9884, 82.9657), "novosibirsk": (54.9884, 82.9657),
    "владивосток": (43.1155, 131.8855), "vladivostok": (43.1155, 131.8855),
    "находка": (42.8274, 132.886), "nakhodka": (42.8274, 132.886),
    "хабаровск": (48.4827, 135.084), "khabarovsk": (48.4827, 135.084),
    "иркутск": (52.2978, 104.2964), "irkutsk": (52.2978, 104.2964),
    "красноярск": (56.0153, 92.8932), "krasnoyarsk": (56.0153, 92.8932),
    "екатеринбург": (56.8389, 60.6057), "yekaterinburg": (56.8389, 60.6057),
    "казань": (55.7887, 49.1221), "kazan": (55.7887, 49.1221),
    "минск": (53.9045, 27.5615), "minsk": (53.9045, 27.5615),
    "алматы": (43.2567, 76.9286), "almaty": (43.2567, 76.9286),
    "астана": (51.1801, 71.446), "astana": (51.1801, 71.446),
    "ташкент": (41.2995, 69.2401), "tashkent": (41.2995, 69.2401),
    "баку": (40.4093, 49.8671), "baku": (40.4093, 49.8671),
    "тбилиси": (41.6938, 44.8015), "tbilisi": (41.6938, 44.8015),
    "шанхай": (31.2304, 121.4737), "shanghai": (31.2304, 121.4737),
    "пекин": (39.9042, 116.4074), "beijing": (39.9042, 116.4074),
    "гуанчжоу": (23.1291, 113.2644), "guangzhou": (23.1291, 113.2644),
    "нинбо": (29.8683, 121.544), "ningbo": (29.8683, 121.544),
    "тяньцзинь": (39.3434, 117.3616), "tianjin": (39.3434, 117.3616),
    "чэнду": (30.5728, 104.0668), "chengdu": (30.5728, 104.0668),
    "иу": (29.3064, 120.0754), "yiwu": (29.3064, 120.0754),
    "харбин": (45.8038, 126.5349), "harbin": (45.8038, 126.5349),
    "урумчи": (43.8256, 87.6169), "urumqi": (43.8256, 87.6169),
    "гонконг": (22.3193, 114.1694), "hong kong": (22.3193, 114.1694),
    "далянь": (38.914, 121.6147), "dalian": (38.914, 121.6147),
    "циндао": (36.0671, 120.3826), "qingdao": (36.0671, 120.3826),
    "берлин": (52.52, 13.405), "berlin": (52.52, 13.405),
    "гамбург": (53.5753, 10.0153), "hamburg": (53.5753, 10.0153),
    "варшава": (52.2297, 21.0122), "warsaw": (52.2297, 21.0122),
    "прага": (50.0755, 14.4378), "prague": (50.0755, 14.4378),
    "вена": (48.2082, 16.3738), "vienna": (48.2082, 16.3738),
    "роттердам": (51.9244, 4.4777), "rotterdam": (51.9244, 4.4777),
    "антверпен": (51.2194, 4.4025), "antwerp": (51.2194, 4.4025),
    "париж": (48.8566, 2.3522), "paris": (48.8566, 2.3522),
    "лондон": (51.5074, -0.1278), "london": (51.5074, -0.1278),
    "стамбул": (41.0082, 28.9784), "istanbul": (41.0082, 28.9784),
    "хельсинки": (60.1699, 24.9384), "helsinki": (60.1699, 24.9384),
    "рига": (56.946, 24.1059), "riga": (56.946, 24.1059),
    "токио": (35.6762, 139.6503), "tokyo": (35.6762, 139.6503),
    "сеул": (37.5665, 126.978), "seoul": (37.5665, 126.978),
    "пусан": (35.1796, 129.0756), "busan": (35.1796, 129.0756),
    "сингапур": (1.3521, 103.8198), "singapore": (1.3521, 103.8198),
    "бангкок": (13.7563, 100.5018), "bangkok": (13.7563, 100.5018),
    "мумбай": (19.076, 72.8777), "mumbai": (19.076, 72.8777),
    "дели": (28.7041, 77.1025), "delhi": (28.7041, 77.1025),
    "дубай": (25.2048, 55.2708), "dubai": (25.2048, 55.2708),
    "джидда": (21.4858, 39.1925), "jeddah": (21.4858, 39.1925),
    "момбаса": (-4.0435, 39.6682), "mombasa": (-4.0435, 39.6682),
    "нью-йорк": (40.7128, -74.006), "new york": (40.7128, -74.006),
    "лос-анджелес": (34.0522, -118.2437), "los angeles": (34.0522, -118.2437),
    "long beach": (33.7701, -118.1937),
    "ванкувер": (49.2827, -123.1207), "vancouver": (49.2827, -123.1207),
    "каир": (30.0444, 31.2357), "cairo": (30.0444, 31.2357),
}


def get_coords(name: str) -> tuple[float, float] | None:
    return CITY_COORDS.get(name.lower().strip())


# ─── Вспомогательные функции ─────────────────────────────────────────────────

def _interp(pts: list, steps: int = 80) -> list:
    if len(pts) < 2:
        return pts
    out = []
    n = len(pts) - 1
    seg_steps = max(6, steps // n)
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        for j in range(seg_steps):
            t = j / seg_steps
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    out.append(pts[-1])
    return [(round(p[0], 5), round(p[1], 5)) for p in out]


# ─── Морские waypoints ───────────────────────────────────────────────────────

_SEA_WP = {
    "suez_s": (29.9, 32.55), "suez_n": (31.25, 32.35), "bab": (12.6, 43.45),
    "hormuz": (26.6, 56.5), "malacca_w": (5.35, 100.3), "malacca_e": (1.25, 104.0),
    "gibraltar": (35.95, -5.45), "bosporus": (41.1, 29.05),
    "med_c": (35.0, 18.0), "indian_c": (-10.0, 72.0),
    "panama_a": (9.35, -79.9), "panama_p": (8.9, -79.5),
    "cape_good": (-34.5, 19.8), "skagerrak": (57.5, 9.0),
    "pacific_c": (10.0, 160.0),
}
W = _SEA_WP


def sea_waypoints(from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> list:
    inMed      = lambda a, o: 30 < a < 47 and -6 < o < 37
    inBlack    = lambda a, o: 40 < a < 47 and 27 < o < 42
    inRedSea   = lambda a, o: 12 < a < 30 and 32 < o < 45
    inPersGulf = lambda a, o: 22 < a < 30 and 47 < o < 60
    inIndian   = lambda a, o: 44 < o < 100 and a < 30
    inEastAsia = lambda o: 100 < o < 150
    inAtlantic = lambda o: -80 < o < 20
    inPacificW = lambda o: o < -80
    inNorthEU  = lambda a, o: a > 54 and 5 < o < 30
    inBCS      = lambda a, o: inBlack(a, o) or (36 < a < 48 and 47 < o < 55)

    needBosph = inBCS(from_lat, from_lon) or inBCS(to_lat, to_lon)
    needSuez  = (
        (inAtlantic(from_lon) or inMed(from_lat, from_lon) or inBCS(from_lat, from_lon)) and
        (inIndian(to_lat, to_lon) or inEastAsia(to_lon) or inRedSea(to_lat, to_lon) or inPersGulf(to_lat, to_lon))
    ) or (
        (inIndian(from_lat, from_lon) or inEastAsia(from_lon) or inRedSea(from_lat, from_lon) or inPersGulf(from_lat, from_lon)) and
        (inAtlantic(to_lon) or inMed(to_lat, to_lon) or inBCS(to_lat, to_lon))
    )
    needMal    = (
        (inIndian(from_lat, from_lon) or needSuez) and inEastAsia(to_lon)
    ) or (inEastAsia(from_lon) and (inIndian(to_lat, to_lon) or needSuez))
    needGib    = (
        (inMed(from_lat, from_lon) and not inMed(to_lat, to_lon) and not inBlack(to_lat, to_lon)) or
        (inMed(to_lat, to_lon) and not inMed(from_lat, from_lon) and not inBlack(from_lat, from_lon))
    )
    needPanama = (
        (inEastAsia(from_lon) or (-80 < from_lon < -60)) and (inPacificW(to_lon) or inAtlantic(to_lon))
    ) or (
        (inEastAsia(to_lon) or (-80 < to_lon < -60)) and (inPacificW(from_lon) or inAtlantic(from_lon))
    )

    via = []
    if needBosph and inBCS(from_lat, from_lon): via.append(W["bosporus"])
    if needGib   and inMed(from_lat, from_lon): via += [W["med_c"], W["gibraltar"]]
    if needSuez:
        if not needGib and inAtlantic(from_lon) and from_lon < 20:
            via += [W["gibraltar"], W["med_c"]]
        via += [W["suez_n"], W["suez_s"], W["bab"]]
        if inPersGulf(to_lat, to_lon) or inPersGulf(from_lat, from_lon):
            via.append(W["hormuz"])
        else:
            via.append(W["indian_c"])
    if needMal:
        via += ([W["malacca_e"], W["malacca_w"]] if inEastAsia(from_lon) else [W["malacca_w"], W["malacca_e"]])
    if needPanama:
        via += ([W["pacific_c"], W["panama_p"], W["panama_a"]] if inEastAsia(from_lon)
                else [W["panama_a"], W["panama_p"], W["pacific_c"]])
    if not any([needSuez, needMal, needPanama, needGib, needBosph]):
        if inNorthEU(from_lat, from_lon) or inNorthEU(to_lat, to_lon):
            via.append(W["skagerrak"])
    if needGib   and inMed(to_lat, to_lon):  via += [W["gibraltar"], W["med_c"]]
    if needBosph and inBCS(to_lat, to_lon):  via.append(W["bosporus"])

    pts = [(from_lat, from_lon)] + list(via) + [(to_lat, to_lon)]
    return _interp(pts, 100)


# ─── Железнодорожные waypoints ───────────────────────────────────────────────

_N = {
    "msk": (55.76, 37.62), "ekb": (56.84, 60.61), "novsib": (54.99, 82.97),
    "krasnoy": (56.02, 92.89), "irkutsk": (52.30, 104.30), "chita": (52.03, 113.50),
    "khabar": (48.48, 135.08), "vlad": (43.12, 131.89), "nakhodka": (42.83, 132.89),
    "almaty": (43.26, 76.93), "astana": (51.18, 71.45), "aktobe": (50.28, 57.21),
    "urumqi": (43.83, 87.62), "xian": (34.34, 108.94), "zhengzhou": (34.75, 113.66),
    "beijing": (39.90, 116.41), "shanghai": (31.23, 121.47), "guangzhou": (23.13, 113.26),
    "chengdu": (30.57, 104.07), "harbin": (45.80, 126.53),
    "warsaw": (52.23, 21.01), "berlin": (52.52, 13.40), "rotterdam": (51.92, 4.48),
    "vienna": (48.21, 16.37), "hamburg": (53.58, 10.02),
    "tashkent": (41.30, 69.24), "tehran": (35.69, 51.39), "istanbul": (41.01, 28.98),
    "tbilisi": (41.69, 44.80), "baku": (40.41, 49.87),
    "seoul": (37.57, 126.98), "busan": (35.18, 129.08), "tokyo": (35.68, 139.65),
}

_CORRIDORS = {
    "china_eu":    [_N["beijing"], _N["zhengzhou"], _N["xian"], _N["urumqi"], (44.8, 80.3), _N["almaty"], _N["astana"], _N["aktobe"], (52, 55), _N["ekb"], _N["msk"], _N["warsaw"], _N["berlin"], _N["rotterdam"]],
    "transsib":    [_N["rotterdam"], _N["berlin"], _N["warsaw"], _N["msk"], _N["ekb"], _N["novsib"], _N["krasnoy"], _N["irkutsk"], _N["chita"], (49.6, 117.5), _N["khabar"], _N["vlad"]],
    "tmtm":        [_N["beijing"], _N["urumqi"], _N["aktobe"], (46, 50.5), _N["baku"], _N["tbilisi"], _N["istanbul"], _N["vienna"], _N["rotterdam"]],
    "ru_eu":       [_N["msk"], _N["warsaw"], _N["berlin"], _N["rotterdam"]],
    "china_ru":    [_N["beijing"], _N["harbin"], (49.6, 117.5), _N["chita"], _N["irkutsk"], _N["novsib"], _N["ekb"], _N["msk"]],
    "korea_eu":    [_N["busan"], _N["seoul"], (42, 130.5), _N["vlad"], _N["khabar"], _N["irkutsk"], _N["novsib"], _N["ekb"], _N["msk"], _N["warsaw"], _N["berlin"]],
    "centasia_eu": [_N["tashkent"], _N["aktobe"], _N["astana"], _N["ekb"], _N["msk"], _N["warsaw"], _N["berlin"]],
}


def rail_waypoints(from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> list:
    def inChina(la, lo):    return 98 < lo < 135 and 18 < la < 55
    def inRussia(la, lo):   return 28 < lo < 145 and 48 < la < 75
    def inEurope(la, lo):   return -5 < lo < 35  and 36 < la < 62
    def inCentAsia(la, lo): return 55 < lo < 90  and 36 < la < 55
    def inFarEast(la, lo):  return lo > 128       and 35 < la < 55
    def inKorea(la, lo):    return 126 < lo < 130 and 34 < la < 39

    corridor = None
    if (inChina(from_lat, from_lon) or inFarEast(from_lat, from_lon)) and (inEurope(to_lat, to_lon) or (inRussia(to_lat, to_lon) and to_lon < 60)):
        corridor = _CORRIDORS["china_eu"]
    elif (inEurope(from_lat, from_lon) or (inRussia(from_lat, from_lon) and from_lon < 60)) and (inChina(to_lat, to_lon) or inFarEast(to_lat, to_lon)):
        corridor = list(reversed(_CORRIDORS["china_eu"]))
    elif inKorea(from_lat, from_lon) and inEurope(to_lat, to_lon):
        corridor = _CORRIDORS["korea_eu"]
    elif inEurope(from_lat, from_lon) and inKorea(to_lat, to_lon):
        corridor = list(reversed(_CORRIDORS["korea_eu"]))
    elif inRussia(from_lat, from_lon) and inFarEast(to_lat, to_lon):
        corridor = _CORRIDORS["transsib"]
    elif inFarEast(from_lat, from_lon) and inRussia(to_lat, to_lon):
        corridor = list(reversed(_CORRIDORS["transsib"]))
    elif inRussia(from_lat, from_lon) and inEurope(to_lat, to_lon):
        corridor = _CORRIDORS["ru_eu"]
    elif inEurope(from_lat, from_lon) and inRussia(to_lat, to_lon):
        corridor = list(reversed(_CORRIDORS["ru_eu"]))
    elif inChina(from_lat, from_lon) and inRussia(to_lat, to_lon):
        corridor = _CORRIDORS["china_ru"]
    elif inCentAsia(from_lat, from_lon) or inCentAsia(to_lat, to_lon):
        corridor = _CORRIDORS["centasia_eu"]
    else:
        return _interp([(from_lat, from_lon), (to_lat, to_lon)], 40)

    def d2(a, b): return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
    fi = min(range(len(corridor)), key=lambda i: d2((from_lat, from_lon), corridor[i]))
    ti = min(range(len(corridor)), key=lambda i: d2((to_lat, to_lon), corridor[i]))
    slc = corridor[fi:ti + 1] if fi <= ti else list(reversed(corridor[ti:fi + 1]))
    pts = [(from_lat, from_lon)] + slc + [(to_lat, to_lon)]
    return _interp(pts, 80)


