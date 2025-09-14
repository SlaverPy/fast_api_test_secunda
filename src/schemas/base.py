from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Базовая схема для всех моделей с общими полями."""
    id: int

    class Config:
        from_attributes = True


class BaseCreateSchema(BaseModel):
    """Базовая схема для создания записей."""
    pass
