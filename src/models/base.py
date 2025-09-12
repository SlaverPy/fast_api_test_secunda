from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """Базовая модель для всех таблиц.

    Добавляет стандартные поля:
    - created_at: дата и время создания записи
    - updated_at: дата и время последнего обновления записи
    """

    __abstract__ = True

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Дата и время создания записи"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Дата и время последнего обновления записи"
    )
