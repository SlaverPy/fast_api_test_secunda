from sqlalchemy import Column, Integer, String, ForeignKey, Table, Index
from sqlalchemy.orm import relationship
from src.models.base import BaseModel, Base

organization_activity = Table(
    "organization_activity",
    Base.metadata,
    Column("organization_id", Integer, ForeignKey("organizations.id"), index=True,
           doc="ID организации"),
    Column("activity_id", Integer, ForeignKey("activities.id"), index=True,
           doc="ID вида деятельности"),
    Index('idx_org_activity', 'organization_id', 'activity_id',
          doc="Составной индекс для связи организация-деятельность")
)


class OrganizationPhone(BaseModel):
    """Телефон организации."""

    __tablename__ = "phones"

    id = Column(Integer, primary_key=True, doc="Уникальный идентификатор телефона")
    number = Column(String(20), nullable=False, doc="Номер телефона организации")
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID организации-владельца"
    )

    organization = relationship("Organization", back_populates="phones",
                                doc="Организация-владелец телефона")

    __table_args__ = (
        Index('idx_org_phone_unique', 'organization_id', 'number', unique=True,
              doc="Уникальный индекс для телефонов в рамках организации"),
    )


class Organization(BaseModel):
    """Организация в справочнике."""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, doc="Уникальный идентификатор организации")
    name = Column(String, nullable=False, unique=True, doc="Название организации")
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False, index=True,
                         doc="ID здания, где находится организация")

    building = relationship("Building", back_populates="organizations",
                            doc="Здание, где расположена организация")
    activities = relationship("Activity", secondary=organization_activity, back_populates="organizations",
                              doc="Виды деятельности организации")
    phones = relationship("OrganizationPhone", back_populates="organization", cascade="all, delete-orphan",
                          doc="Телефоны организации")

    __table_args__ = (
        Index('idx_org_building', 'building_id',
              doc="Индекс для поиска организаций по зданию"),
        Index('idx_org_name', 'name',
              doc="Индекс для поиска организаций по названию"),
    )
