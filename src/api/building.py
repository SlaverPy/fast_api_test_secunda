import logging

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.core.database import get_session
from src.models.building import Building as BuildingModel
from src.schemas.building import Building, BuildingCreate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/buildings", tags=["Здания"])


@router.get("/", response_model=list[Building])
async def list_buildings(
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
        session: AsyncSession = get_session()
):
    """
    Получить список всех зданий с пагинацией.
    """
    try:
        logger.info("Запрошен список всех зданий")

        query = select(BuildingModel).offset((page - 1) * size).limit(size)
        result = await session.execute(query)
        buildings = result.scalars().all()

        count_result = await session.execute(select(func.count()).select_from(BuildingModel))
        total = count_result.scalar()

        logger.debug(f"Найдено зданий: {len(buildings)} из {total}")
        return buildings

    except Exception as e:
        logger.error(f"Ошибка при получении списка зданий: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/", response_model=Building)
async def create_building(data: BuildingCreate, session: AsyncSession = get_session()):
    """
    Создать новое здание.
    """
    try:
        logger.info(f"Создание нового здания: {data.address}")

        existing_building = await session.execute(
            select(BuildingModel).where(
                (BuildingModel.latitude == data.latitude) &
                (BuildingModel.longitude == data.longitude)
            )
        )
        if existing_building.scalar():
            raise HTTPException(status_code=400, detail="Здание с такими координатами уже существует")

        new_building = BuildingModel(
            address=data.address,
            latitude=data.latitude,
            longitude=data.longitude
        )
        session.add(new_building)
        await session.commit()
        await session.refresh(new_building)

        logger.info(f"Здание создано с ID={new_building.id}")
        return new_building

    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при создании здания: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/{building_id}", response_model=Building)
async def get_building(building_id: int, session: AsyncSession = get_session()):
    """
    Получить здание по его идентификатору.
    """
    try:
        logger.info(f"Запрошено здание ID={building_id}")

        building = await session.get(BuildingModel, building_id)
        if not building:
            logger.warning(f"Здание ID={building_id} не найдено")
            raise HTTPException(status_code=404, detail="Здание не найдено")

        logger.debug(f"Здание найдено: {building.address}")
        return building

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении здания {building_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
