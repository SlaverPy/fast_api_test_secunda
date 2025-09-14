from pydantic import Field

from .base import BaseSchema, BaseCreateSchema


class BuildingBase(BaseCreateSchema):
    """Базовая схема для здания."""
    address: str = Field(..., description="Адрес здания")
    latitude: float = Field(..., description="Географическая широта")
    longitude: float = Field(..., description="Географическая долгота")


class BuildingCreate(BuildingBase):
    """Схема для создания нового здания."""
    pass


class Building(BuildingBase, BaseSchema):
    """Схема для возврата данных о здании."""
    pass
