from pydantic import Field

from .base import BaseSchema, BaseCreateSchema


class ActivityBase(BaseCreateSchema):
    """Базовая схема для вида деятельности."""
    name: str = Field(..., description="Название вида деятельности")
    parent_id: int | None = Field(None, description="ID родительского вида деятельности")
    level: int = Field(0, ge=0, le=2, description="Уровень вложенности (0-2)")


class ActivityCreate(ActivityBase):
    """Схема для создания нового вида деятельности."""
    pass


class Activity(ActivityBase, BaseSchema):
    """Схема для возврата данных о виде деятельности."""
    pass


class ActivityWithChildren(Activity):
    """Схема для возврата вида деятельности с дочерними элементами."""
    children: list['ActivityWithChildren'] = []


ActivityWithChildren.model_rebuild()
