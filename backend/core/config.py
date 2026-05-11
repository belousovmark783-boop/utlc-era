"""
Конфигурация приложения.
Читает переменные из .env / окружения через pydantic-settings.
"""
import os
from pathlib import Path
from typing import List

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass


class Settings:
    APP_TITLE: str    = os.getenv("APP_TITLE",   "UTLC ERA API")
    APP_VERSION: str  = os.getenv("APP_VERSION", "2.1.0")
    DB_HOST: str      = os.getenv("DB_HOST",     "localhost")
    DB_PORT: int      = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str      = os.getenv("DB_NAME",     "utlc_era")
    DB_USER: str      = os.getenv("DB_USER",     "postgres")
    DB_PASSWORD: str  = os.getenv("DB_PASSWORD", "")
    DB_SSLMODE: str   = os.getenv("DB_SSLMODE",  "prefer")
    HOST: str         = os.getenv("HOST",        "0.0.0.0")
    PORT: int         = int(os.getenv("PORT",    "8000"))
    DEBUG: bool       = os.getenv("DEBUG", "false").lower() == "true"

    # API-ключ для доступа к эндпоинтам (опционально).
    # Если задан — все /api/* запросы требуют заголовок X-API-Key.
    API_KEY: str      = os.getenv("API_KEY", "")

    # CORS: задаётся через CORS_ORIGINS="http://a.com,http://b.com"
    # или через ALLOWED_ORIGINS (обратная совместимость).
    @property
    def CORS_ORIGINS(self) -> List[str]:
        raw = os.getenv(
            "CORS_ORIGINS",
            os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000"),
        )
        return [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()
