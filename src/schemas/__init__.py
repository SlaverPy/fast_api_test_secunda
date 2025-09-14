# schemas/__init__.py
"""
Модуль схем Pydantic для валидации данных API.

Содержит схемы для:
- Activity: Виды деятельности организаций
- Building: Здания с организациями
- Organization: Организации и их телефоны
- Поисковые запросы: Поиск по координатам и радиусу
- Ответы API: Пагинация, ошибки, успешные операции
"""

from .activity import ActivityBase, ActivityCreate, Activity, ActivityWithChildren
from .building import BuildingBase, BuildingCreate, Building
from .organization import (
    OrganizationPhoneBase,
    OrganizationPhoneCreate,
    OrganizationPhone,
    OrganizationBase,
    OrganizationCreate,
    OrganizationUpdate,
    Organization,
    OrganizationWithBuilding,
    OrganizationWithActivities
)
from .search import CoordinateRange, RadiusSearch
from .response import PaginatedResponse, ErrorResponse, SuccessResponse


__all__ = [
    'ActivityBase',
    'ActivityCreate',
    'Activity',
    'ActivityWithChildren',
    'BuildingBase',
    'BuildingCreate',
    'Building',
    'OrganizationPhoneBase',
    'OrganizationPhoneCreate',
    'OrganizationPhone',
    'OrganizationBase',
    'OrganizationCreate',
    'OrganizationUpdate',
    'Organization',
    'OrganizationWithBuilding',
    'OrganizationWithActivities',
    'CoordinateRange',
    'RadiusSearch',
    'PaginatedResponse',
    'ErrorResponse',
    'SuccessResponse'
]