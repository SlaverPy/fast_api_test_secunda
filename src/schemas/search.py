from pydantic import BaseModel, Field


class CoordinateRange(BaseModel):
    """
    Схема для поиска в прямоугольной области по координатам.
    """
    min_lat: float = Field(..., description="Минимальная широта")
    max_lat: float = Field(..., description="Максимальная широта")
    min_lng: float = Field(..., description="Минимальная долгота")
    max_lng: float = Field(..., description="Максимальная долгота")


class RadiusSearch(BaseModel):
    """
    Схема для поиска в радиусе от указанной точки.
    """
    latitude: float = Field(..., description="Центральная точка - широта")
    longitude: float = Field(..., description="Центральная точка - долгота")
    radius_km: float = Field(..., gt=0, description="Радиус поиска в километрах")
