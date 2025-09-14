import logging

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from src.core.database import get_session
from src.models.organization import Organization as OrganizationModel
from src.models.building import Building as BuildingModel
from src.models.activity import Activity as ActivityModel
from src.models import OrganizationPhone as PhoneModel
from src.schemas import PaginatedResponse
from src.schemas.organization import (
    Organization, OrganizationCreate, OrganizationUpdate
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/organizations", tags=["Организации"])


@router.get("/", response_model=PaginatedResponse)
async def list_organizations(
        building_id: int | None = Query(None, description="Фильтр по ID здания"),
        activity_id: int | None = Query(None, description="Фильтр по ID вида деятельности"),
        name: str | None = Query(None, description="Поиск по названию организации"),
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
        session: AsyncSession = get_session()
):
    """
    Получить список организаций с фильтрацией и пагинацией.
    """
    try:
        logger.info("Запрошен список организаций с фильтрацией и пагинацией")

        query = select(OrganizationModel).options(
            selectinload(OrganizationModel.building),
            selectinload(OrganizationModel.activities),
            selectinload(OrganizationModel.phones)
        )

        conditions = []
        if building_id:
            conditions.append(OrganizationModel.building_id == building_id)
        if name:
            conditions.append(OrganizationModel.name.ilike(f"%{name}%"))
        if activity_id:
            query = query.join(OrganizationModel.activities).where(ActivityModel.id == activity_id)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset((page - 1) * size).limit(size)
        result = await session.execute(query)
        items = result.scalars().all()

        count_query = select(func.count()).select_from(OrganizationModel)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        if activity_id:
            count_query = count_query.join(OrganizationModel.activities).where(ActivityModel.id == activity_id)

        total_result = await session.execute(count_query)
        total = total_result.scalar()

        logger.debug(f"Пагинация: страница {page}, элементов {len(items)}, всего {total}")

        return PaginatedResponse(
            total=total,
            page=page,
            size=size,
            items=items
        )

    except Exception as e:
        logger.error(f"Ошибка при получении списка организаций: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/{org_id}", response_model=Organization)
async def get_organization(org_id: int, session: AsyncSession = get_session()):
    """
    Получить организацию по ID, включая здание, телефоны и виды деятельности.
    """
    try:
        logger.info(f"Запрошена организация ID={org_id}")

        org = await session.get(
            OrganizationModel,
            org_id,
            options=[
                selectinload(OrganizationModel.building),
                selectinload(OrganizationModel.activities),
                selectinload(OrganizationModel.phones)
            ]
        )

        if not org:
            logger.warning(f"Организация ID={org_id} не найдена")
            raise HTTPException(status_code=404, detail="Организация не найдена")

        logger.debug(f"Организация найдена: {org.name}")
        return org

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении организации {org_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/", response_model=Organization)
async def create_organization(data: OrganizationCreate, session: AsyncSession = get_session()):
    """
    Создать новую организацию с телефонами и видами деятельности.
    """
    try:
        logger.info(f"Создание организации: {data.name}")

        building = await session.get(BuildingModel, data.building_id)
        if not building:
            logger.warning(f"Здание ID={data.building_id} не найдено")
            raise HTTPException(status_code=404, detail="Здание не найдено")

        new_org = OrganizationModel(
            name=data.name,
            building_id=data.building_id
        )
        session.add(new_org)
        await session.flush()

        for phone in data.phones:
            new_phone = PhoneModel(number=phone.number, organization_id=new_org.id)
            session.add(new_phone)

        if data.activity_ids:
            activities = await session.execute(
                select(ActivityModel).where(ActivityModel.id.in_(data.activity_ids))
            )
            new_org.activities = activities.scalars().all()

        await session.commit()
        await session.refresh(new_org)

        logger.info(f"Организация создана с ID={new_org.id}")
        return new_org

    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при создании организации: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.put("/{org_id}", response_model=Organization)
async def update_organization(org_id: int, data: OrganizationUpdate, session: AsyncSession = get_session()):
    """
    Обновить организацию по ID.
    """
    try:
        logger.info(f"Обновление организации ID={org_id}")

        org = await session.get(
            OrganizationModel,
            org_id,
            options=[
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities)
            ]
        )

        if not org:
            logger.warning(f"Организация ID={org_id} не найдена")
            raise HTTPException(status_code=404, detail="Организация не найдена")

        if data.name is not None:
            org.name = data.name

        if data.building_id is not None:
            building = await session.get(BuildingModel, data.building_id)
            if not building:
                logger.warning(f"Здание ID={data.building_id} не найдено")
                raise HTTPException(status_code=404, detail="Здание не найдено")
            org.building_id = data.building_id

        if data.activity_ids is not None:
            activities = await session.execute(
                select(ActivityModel).where(ActivityModel.id.in_(data.activity_ids))
            )
            org.activities = activities.scalars().all()

        if data.phones is not None:
            for phone in org.phones:
                await session.delete(phone)
            for phone in data.phones:
                new_phone = PhoneModel(number=phone.number, organization_id=org.id)
                session.add(new_phone)

        await session.commit()
        await session.refresh(org)

        logger.info(f"Организация обновлена ID={org.id}")
        return org

    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при обновлении организации {org_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
