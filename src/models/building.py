from sqlalchemy import Column, Integer, String, Float, Index
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class Building(BaseModel):
    """Здание, в котором располагаются организации."""

    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, doc="Уникальный идентификатор здания")
    address = Column(String, nullable=False, unique=True, doc="Адрес здания")
    latitude = Column(Float, nullable=False, doc="Географическая широта")
    longitude = Column(Float, nullable=False, doc="Географическая долгота")

    organizations = relationship("Organization", back_populates="building",
                                 doc="Организации, расположенные в этом здании")

    __table_args__ = (
        Index('idx_building_coords_unique', 'latitude', 'longitude', unique=True,
              doc="Уникальный индекс для координат здания"),
        Index('idx_building_coords', 'latitude', 'longitude',
              doc="Индекс для географического поиска"),
    )
