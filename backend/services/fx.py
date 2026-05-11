"""
Курсы валют через frankfurter.app (бесплатно, без ключа).
Конвертирует ставку перевозчика в USD если она указана в другой валюте.
"""
import httpx

_TIMEOUT   = 5.0
_BASE_URL  = "https://api.frankfurter.app"

# Кэш на сессию чтобы не дёргать API на каждый маршрут
_cache: dict[str, float] = {}

# Поддерживаемые валюты с человекочитаемыми названиями
SUPPORTED_CURRENCIES = {
    "USD": "Доллар США",
    "EUR": "Евро",
    "CNY": "Китайский юань",
    "RUB": "Российский рубль",
    "KZT": "Казахстанский тенге",
    "JPY": "Японская иена",
    "GBP": "Британский фунт",
    "CHF": "Швейцарский франк",
    "TRY": "Турецкая лира",
    "AED": "Дирхам ОАЭ",
}


async def get_rate_to_usd(currency: str) -> float:
    """
    Возвращает курс currency → USD.
    Например get_rate_to_usd('EUR') → 1.08 (1 EUR = 1.08 USD).
    Если валюта уже USD или запрос упал — возвращает 1.0.
    """
    currency = currency.upper().strip()
    if currency == "USD":
        return 1.0

    if currency in _cache:
        return _cache[currency]

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{_BASE_URL}/latest",
                params={"from": currency, "to": "USD"},
            )
            if resp.status_code == 200:
                rate = resp.json()["rates"]["USD"]
                _cache[currency] = rate
                return rate
    except Exception:
        pass

    # Фоллбэк — приблизительные курсы на случай недоступности API
    fallback = {
        "EUR": 1.08, "CNY": 0.138, "RUB": 0.011,
        "KZT": 0.0022, "JPY": 0.0067, "GBP": 1.27,
        "CHF": 1.12, "TRY": 0.031, "AED": 0.272,
    }
    return fallback.get(currency, 1.0)


async def convert_to_usd(amount: float, currency: str) -> dict:
    """
    Конвертирует сумму в USD.
    Возвращает {'usd': float, 'rate': float, 'original': float, 'currency': str}
    """
    rate = await get_rate_to_usd(currency)
    return {
        "usd":      round(amount * rate, 2),
        "rate":     rate,
        "original": amount,
        "currency": currency.upper(),
    }
