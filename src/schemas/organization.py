from pydantic import Field

from .activity import Activity
from .building import Building
from .base import BaseSchema, BaseCreateSchema


class OrganizationPhoneBase(BaseCreateSchema):
    """Базовая схема для телефона организации."""

    number: str = Field(
        ...,
        max_length=20,
        description="Номер телефона организации",
        examples=["+7-123-456-7890", "8-800-555-3535"]
    )


class OrganizationPhoneCreate(OrganizationPhoneBase):
    """Схема для создания нового телефона организации."""
    pass


class OrganizationPhone(OrganizationPhoneBase, BaseSchema):
    """Схема для возврата данных о телефоне организации."""
    organization_id: int = Field(..., description="ID организации-владельца")


class OrganizationBase(BaseCreateSchema):
    """Базовая схема для организации."""
    name: str = Field(
        ...,
        description="Название организации",
        examples=["ООО «Рога и Копыта»", "ИП Иванов"]
    )
    building_id: int = Field(..., description="ID здания, где находится организация")


class OrganizationCreate(OrganizationBase):
    """Схема для создания новой организации."""
    activity_ids: list[int] = Field(
        default_factory=list,
        description="ID видов деятельности организации"
    )
    phones: list[OrganizationPhoneCreate] = Field(
        default_factory=list,
        description="Телефоны организации"
    )


class OrganizationUpdate(BaseCreateSchema):
    """Схема для обновления данных организации."""
    name: str | None = Field(
        None,
        description="Новое название организации",
        examples=["ООО «Новое название»"]
    )
    building_id: int | None = Field(None, description="Новый ID здания")
    activity_ids: list[int] | None = Field(None, description="Новые ID видов деятельности")
    phones: list[OrganizationPhoneCreate] | None = Field(None, description="Новые телефоны организации")


class Organization(OrganizationBase, BaseSchema):
    """Схема для возврата полных данных об организации."""
    building: Building = Field(..., description="Здание, где расположена организация")
    activities: list[Activity] = Field(..., description="Виды деятельности организации")
    phones: list[OrganizationPhone] = Field(..., description="Телефоны организации")


class OrganizationWithBuilding(Organization):
    """Схема для возврата организации с полными данными о здании."""
    pass


class OrganizationWithActivities(Organization):
    """Схема для возврата организации с полными данными о видах деятельности."""
    pass
