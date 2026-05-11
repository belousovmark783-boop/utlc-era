"""
Pydantic схемы для упрощённого ввода логиста
"""
from typing import Literal
from pydantic import BaseModel, Field


class CargoParams(BaseModel):
    weight_tons:  float = Field(gt=0,  description="Вес груза в тоннах")
    volume_teu:   float = Field(gt=0,  default=1.0, description="Объём в TEU (1 TEU = 20 футов)")
    cargo_value:  float = Field(gt=0,  description="Стоимость груза в USD")
    cargo_type:   str   = Field(default="обычный",
                                description="Тип груза: обычный / опасный / скоропортящийся")
    capital_rate: float = Field(default=15.0, gt=0, description="Ставка WACC, %")


class RouteInput(BaseModel):
    """Один маршрут — вводится логистом вручную."""
    route_id:     str
    origin:       str  = Field(description="Город отправки")
    destination:  str  = Field(description="Город назначения")
    mode:         Literal["sea", "rail"]
    carrier_rate_usd: float = Field(default=0.0, ge=0, description="Ставка перевозчика в USD (0 = взять индикативную автоматически)")
    currency:     str  = Field(default="USD", description="Валюта ставки перевозчика")


class SimpleAnalyzeRequest(BaseModel):
    """Упрощённый запрос анализа — без CSV, без ручных рисков."""
    routes:       list[RouteInput]
    cargo:        CargoParams
    weights:      "Weights | None" = None


class EnrichRequest(BaseModel):
    """Запрос на обогащение одного маршрута внешними данными."""
    origin:      str
    destination: str
    mode:        Literal["sea", "rail"]


class EnrichResponse(BaseModel):
    """Ответ с автоматически рассчитанными параметрами маршрута."""
    origin:      str
    destination: str
    mode:        str
    distance_km:             float
    transit_days:            int
    geo_risk:                float
    weather_risk:            float
    congestion:              float
    emission_factor:         float
    border_crossings:        int
    port_calls:              int
    gauge_changes:           int
    customs_fee_per_border:  float
    handling_fee_per_port:   float
    carbon_price:            float
    weather_details:         list
    geo_details:             dict


# Импортируем Weights из основных схем
from schemas.analysis import Weights
SimpleAnalyzeRequest.model_rebuild()
