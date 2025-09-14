from pydantic import BaseModel, Field


class PaginatedResponse(BaseModel):
    """
    Схема для пагинированного ответа.
    """
    total: int = Field(..., description="Общее количество элементов")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Количество элементов на странице")
    items: list = Field(..., description="Список элементов текущей страницы")


class ErrorResponse(BaseModel):
    """
    Схема для ответа с ошибкой.
    """
    detail: str = Field(..., description="Описание ошибки")


class SuccessResponse(BaseModel):
    """
    Схема для успешного ответа.
    """
    message: str = Field(..., description="Сообщение об успешном выполнении операции")
