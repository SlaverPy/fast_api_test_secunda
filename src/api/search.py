import logging

from fastapi import Body, Query, APIRouter, HTTPException
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.search import CoordinateRange, RadiusSearch
from src.schemas.response import PaginatedResponse
from src.models.building import Building as BuildingModel
from src.models import Organization as OrganizationModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["Поиск"])


@router.post("/rectangle", response_model=PaginatedResponse)
async def search_organizations_rectangle(
        coords: CoordinateRange = Body(..., description="Координаты прямоугольной области"),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        session: AsyncSession = get_session()
):
    """
    Найти организации в заданной прямоугольной области.
    """
    try:
        logger.info(f"Поиск организаций в прямоугольной области: {coords}")

        query = select(OrganizationModel).join(BuildingModel).where(
            and_(
                BuildingModel.latitude >= coords.min_lat,
                BuildingModel.latitude <= coords.max_lat,
                BuildingModel.longitude >= coords.min_lng,
                BuildingModel.longitude <= coords.max_lng
            )
        ).offset((page - 1) * size).limit(size)

        result = await session.execute(query)
        items = result.scalars().all()

        count_query = select(func.count()).join(BuildingModel).where(
            and_(
                BuildingModel.latitude >= coords.min_lat,
                BuildingModel.latitude <= coords.max_lat,
                BuildingModel.longitude >= coords.min_lng,
                BuildingModel.longitude <= coords.max_lng
            )
        )
        total_result = await session.execute(count_query)
        total = total_result.scalar()

        logger.debug(f"Найдено организаций в прямоугольной области: {total}")
        return PaginatedResponse(total=total, page=page, size=size, items=items)

    except Exception as e:
        logger.error(f"Ошибка при поиске в прямоугольной области: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/radius", response_model=PaginatedResponse)
async def search_organizations_radius(
        params: RadiusSearch = Body(..., description="Центр и радиус поиска"),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        session: AsyncSession = get_session()
):
    """
    Найти организации в заданном радиусе от указанной точки.
    """
    try:
        logger.info(
            f"Поиск организаций в радиусе {params.radius_km} км от точки ({params.latitude}, {params.longitude})")

        distance_expr = (
                6371 * func.acos(
            func.cos(func.radians(params.latitude)) *
            func.cos(func.radians(BuildingModel.latitude)) *
            func.cos(func.radians(BuildingModel.longitude) - func.radians(params.longitude)) +
            func.sin(func.radians(params.latitude)) *
            func.sin(func.radians(BuildingModel.latitude))
        )
        )

        query = select(OrganizationModel).join(BuildingModel).where(
            distance_expr <= params.radius_km
        ).offset((page - 1) * size).limit(size)

        result = await session.execute(query)
        items = result.scalars().all()

        count_query = select(func.count()).join(BuildingModel).where(
            distance_expr <= params.radius_km
        )
        total_result = await session.execute(count_query)
        total = total_result.scalar()

        logger.debug(f"Найдено организаций в радиусе: {total}")
        return PaginatedResponse(total=total, page=page, size=size, items=items)

    except Exception as e:
        logger.error(f"Ошибка при поиске по радиусу: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
