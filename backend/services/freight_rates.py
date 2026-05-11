"""
Индикативные ставки фрахта по коридорам.

Источники (в порядке приоритета):
  1. Море  — Freightos FBX API (https://developer.freightos.com)
             Регистрация бесплатна; ключ задаётся через FBX_API_KEY в .env
  2. ЖД    — ERAI Index (https://index1520.com) — продукт UTLC ERA
             При наличии договорного доступа: ERAI_API_KEY в .env
  3. Fallback — публичные индикаторы Q1 2025 (Drewry, Xeneta, UTLC пресс-релизы)

Все суммы — USD за TEU (20ft-эквивалент), если не указано иное.
"""

import os
import httpx

_TIMEOUT = 6.0

# ─── Env keys ────────────────────────────────────────────────────────────────
FBX_API_KEY  = os.getenv("FBX_API_KEY", "")
ERAI_API_KEY = os.getenv("ERAI_API_KEY", "")

# ─── Freightos FBX endpoints ─────────────────────────────────────────────────
_FBX_BASE    = "https://api.freightos.com/fbx/v1"
_FBX_INDICES = {
    # (region_from, region_to): FBX index code
    ("china",        "europe"):        "FBX11",   # China/East Asia → North Europe
    ("china",        "north_america"): "FBX01",   # China/East Asia → US West Coast
    ("europe",       "china"):         "FBX11",
    ("north_america","china"):         "FBX01",
    ("korea",        "europe"):        "FBX11",
    ("korea",        "north_america"): "FBX01",
    ("china",        "russia"):        None,       # нет прямого FBX индекса
    ("middle_east",  "europe"):        "FBX31",   # Middle East/India → North Europe
}

# ─── ERAI (UTLC ERA) endpoint ─────────────────────────────────────────────────
_ERAI_BASE = "https://api.index1520.com/v1"  # гипотетический endpoint; уточняйте у UTLC ERA

# ─── Fallback: индикативные ставки Q1 2025 (USD / TEU) ───────────────────────
# Источники: Drewry WCI, Xeneta, UTLC ERA пресс-релизы, Freightos публичные данные
_FALLBACK_RATES: dict[tuple, dict] = {
    # Море
    ("china",        "europe",        "sea"):  {"rate": 3200, "source": "Drewry WCI Q1-2025", "note": "~$2 800–3 800"},
    ("china",        "north_america", "sea"):  {"rate": 2800, "source": "Drewry WCI Q1-2025", "note": "~$2 400–3 200"},
    ("korea",        "europe",        "sea"):  {"rate": 3400, "source": "Drewry WCI Q1-2025", "note": "~$3 000–3 900"},
    ("middle_east",  "europe",        "sea"):  {"rate": 1800, "source": "Xeneta Q1-2025",     "note": "~$1 400–2 200"},
    ("china",        "russia",        "sea"):  {"rate": 1200, "source": "Market est. Q1-2025","note": "~$900–1 500"},
    ("russia",       "europe",        "sea"):  {"rate": 1100, "source": "Market est. Q1-2025","note": "~$800–1 400"},
    # ЖД (источник: UTLC ERA пресс-релизы, ERAI index 2024–2025)
    ("china",        "europe",        "rail"): {"rate": 3800, "source": "ERAI / UTLC ERA 2025","note": "~$3 200–4 500 в зависимости от направления"},
    ("china",        "russia",        "rail"): {"rate": 1600, "source": "ERAI / UTLC ERA 2025","note": "~$1 200–2 000"},
    ("russia",       "europe",        "rail"): {"rate": 1400, "source": "ERAI / UTLC ERA 2025","note": "~$1 100–1 700"},
    ("korea",        "europe",        "rail"): {"rate": 4200, "source": "ERAI / UTLC ERA 2025","note": "~$3 800–4 800"},
    ("central_asia", "europe",        "rail"): {"rate": 2800, "source": "ERAI / UTLC ERA 2025","note": "~$2 400–3 200"},
}


async def _fetch_fbx(region_from: str, region_to: str) -> dict | None:
    """
    Получает актуальную ставку Freightos FBX для коридора.
    Возвращает None если ключ не задан или запрос не удался.
    """
    if not FBX_API_KEY:
        return None

    index_code = _FBX_INDICES.get((region_from, region_to)) or \
                 _FBX_INDICES.get((region_to, region_from))
    if not index_code:
        return None

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{_FBX_BASE}/rates/{index_code}",
                headers={"Authorization": f"Bearer {FBX_API_KEY}"},
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "rate":   data.get("rate") or data.get("price"),
                    "source": f"Freightos FBX {index_code} (live)",
                    "note":   f"Дата: {data.get('date', '—')}",
                }
    except Exception:
        pass

    return None


async def _fetch_erai(region_from: str, region_to: str) -> dict | None:
    """
    Получает индикатор ERAI (UTLC ERA) для ж/д коридора.
    Возвращает None если ключ не задан или запрос не удался.
    """
    if not ERAI_API_KEY:
        return None

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{_ERAI_BASE}/corridor-rate",
                params={"from": region_from, "to": region_to},
                headers={"X-API-Key": ERAI_API_KEY},
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "rate":   data.get("rate_usd"),
                    "source": "ERAI Index (UTLC ERA, live)",
                    "note":   f"Дата: {data.get('date', '—')}",
                }
    except Exception:
        pass

    return None


async def get_indicative_rate(
    region_from: str,
    region_to: str,
    mode: str,
    weight_tons: float = 1.0,
) -> dict:
    """
    Возвращает индикативную ставку фрахта (USD) для коридора.

    Args:
        region_from:  регион отправки ('china', 'europe', ...)
        region_to:    регион назначения
        mode:         'sea' | 'rail'
        weight_tons:  вес груза в тоннах

    Returns:
        {
          "rate_usd": float,       # ставка за TEU
          "source":   str,         # источник данных
          "note":     str,         # диапазон / дата
          "is_live":  bool,        # True если из API, False если fallback
        }
    """
    live_data = None
    if mode == "sea":
        live_data = await _fetch_fbx(region_from, region_to)
    elif mode == "rail":
        live_data = await _fetch_erai(region_from, region_to)

    if live_data and live_data.get("rate"):
        return {
            "rate_usd": float(live_data["rate"]),
            "source":   live_data["source"],
            "note":     live_data.get("note", ""),
            "is_live":  True,
        }

    # Fallback: ищем в обоих направлениях
    fb = (
        _FALLBACK_RATES.get((region_from, region_to, mode)) or
        _FALLBACK_RATES.get((region_to, region_from, mode))
    )

    if fb:
        return {
            "rate_usd": float(fb["rate"]),
            "source":   fb["source"],
            "note":     fb["note"],
            "is_live":  False,
        }

    # Совсем нет данных — дефолт по режиму
    defaults = {"sea": 2500.0, "rail": 3000.0}
    return {
        "rate_usd": defaults.get(mode, 2000.0),
        "source":   "Оценка (нет данных по коридору)",
        "note":     "Требует уточнения у перевозчика",
        "is_live":  False,
    }
