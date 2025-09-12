from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class Activity(BaseModel):
    """Вид деятельности организации (древовидная структура до 3 уровней)."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, doc="Уникальный идентификатор вида деятельности")
    name = Column(String, nullable=False, doc="Название вида деятельности")
    parent_id = Column(Integer, ForeignKey("activities.id"), nullable=True, index=True,
                       doc="Ссылка на родительский вид деятельности")
    level = Column(Integer, nullable=False, default=0, doc="Уровень вложенности (0-2)")

    # Relationships
    parent = relationship("Activity", remote_side=[id], backref="children")
    organizations = relationship("Organization", secondary="organization_activity", back_populates="activities",
                                 doc="Организации, занимающиеся этим видом деятельности")

    __table_args__ = (
        CheckConstraint('level BETWEEN 0 AND 2', name='check_level_range'),
    )
