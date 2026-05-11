"""
Pydantic схемы для анализа маршрутов
"""
from pydantic import BaseModel, Field


class Weights(BaseModel):
    cost:      float = Field(default=0.30, ge=0, le=1)
    time:      float = Field(default=0.50, ge=0, le=1)
    risk:      float = Field(default=0.20, ge=0, le=1)
    emissions: float = Field(default=0.0,  ge=0, le=1)


class AnalyzeRequest(BaseModel):
    csv_content:  str
    cargo_value:  float = Field(default=250_000, gt=0)
    capital_rate: float = Field(default=15.0, gt=0)
    weights:      Weights = Weights()


class CostBreakdown(BaseModel):
    base:        float
    customs:     float
    handling:    float
    carbon:      float
    insurance:   float
    working_cap: float
    inventory:   float
    admin:       float
    contingency: float


class RouteResult(BaseModel):
    route_id:    str
    mode:        str
    origin:      str
    destination: str
    cost_usd:    float
    time_days:   int
    risk_index:  float
    emissions:   float
    score:       float
    breakdown:   CostBreakdown


class AnalyzeResponse(BaseModel):
    id:           int
    results:      list[RouteResult]
    weights:      Weights
    cargo_value:  float
    capital_rate: float
