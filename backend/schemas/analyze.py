"""
schemas/analyze.py — Pydantic-модели для запроса анализа и ответов.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any


# ─────────────────────────────────────────────
# Request schemas
# ─────────────────────────────────────────────

class WeightsSchema(BaseModel):
    cost:      float = Field(0.30, ge=0, le=1)
    time:      float = Field(0.50, ge=0, le=1)
    risk:      float = Field(0.20, ge=0, le=1)
    emissions: float = Field(0.00, ge=0, le=1)


class AnalyzeRequest(BaseModel):
    csv_content:  str
    cargo_value:  float = Field(250_000, gt=0, description="Стоимость груза, USD")
    capital_rate: float = Field(15.0, gt=0, description="Ставка капитала, %")
    weights:      WeightsSchema = WeightsSchema()


# ─────────────────────────────────────────────
# Response schemas
# ─────────────────────────────────────────────

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
    results:      List[RouteResult]
    weights:      Dict[str, float]
    cargo_value:  float
    capital_rate: float
