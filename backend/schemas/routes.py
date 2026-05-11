"""
Pydantic схемы для геометрии маршрутов
"""
from pydantic import BaseModel


class RouteGeomRequest(BaseModel):
    origin:      str
    destination: str
    mode:        str  # sea | rail
