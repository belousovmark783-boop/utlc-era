"""
UTLC ERA v2.1 — FastAPI Backend
Entry point: initializes app, registers routers, starts server.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import settings
from db.database import init_db
from routers import analyze, history, reports, geometry, health, simple


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при старте — работает и под uvicorn, и под gunicorn."""
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description="Route comparison and TCO analysis API",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Опциональная защита по API-ключу.
    # Включается когда в окружении задан API_KEY=<secret>.
    if settings.API_KEY:
        @app.middleware("http")
        async def api_key_middleware(request: Request, call_next):
            # /health и /docs доступны без ключа
            if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
                return await call_next(request)
            key = request.headers.get("X-API-Key", "")
            if key != settings.API_KEY:
                raise HTTPException(status_code=401, detail="Invalid or missing API key")
            return await call_next(request)

    # Register routers
    app.include_router(health.router, tags=["health"])
    app.include_router(analyze.router, prefix="/api", tags=["analyze"])
    app.include_router(history.router, prefix="/api", tags=["history"])
    app.include_router(reports.router, prefix="/api", tags=["reports"])
    app.include_router(geometry.router, prefix="/api", tags=["geometry"])
    app.include_router(simple.router,   prefix="/api", tags=["simple"])

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
