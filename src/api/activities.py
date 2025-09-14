import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_session
from src.models.activity import Activity as ActivityModel
from src.schemas.activity import ActivityWithChildren, Activity, ActivityCreate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/activities", tags=["Деятельности"])


@router.get("/", response_model=list[ActivityWithChildren])
async def list_activities(session: AsyncSession = get_session()):
    """
    Получить список всех видов деятельности с дочерними элементами.
    """
    try:
        logger.info("Запрошен список всех видов деятельности с дочерними элементами")

        result = await session.execute(select(ActivityModel).where(ActivityModel.parent_id == None))
        root_activities = result.scalars().all()

        async def build_tree(activity: ActivityModel, current_level: int = 0,
                             max_level: int = 2) -> ActivityWithChildren:
            """Рекурсивно строит дерево активности."""
            children_list = []
            if current_level < max_level:
                result = await session.execute(select(ActivityModel).where(ActivityModel.parent_id == activity.id))
                children = result.scalars().all()
                for child in children:
                    children_list.append(await build_tree(child, current_level + 1, max_level))

            return ActivityWithChildren(
                id=activity.id,
                name=activity.name,
                parent_id=activity.parent_id,
                level=current_level,
                children=children_list
            )

        tree = []
        for act in root_activities:
            tree.append(await build_tree(act))

        logger.debug(f"Сформировано дерево видов деятельности, корневых элементов: {len(tree)}")
        return tree

    except Exception as e:
        logger.error(f"Ошибка при получении списка видов деятельности: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/", response_model=Activity)
async def create_activity(data: ActivityCreate, session: AsyncSession = get_session()):
    """
    Создать новый вид деятельности.
    """
    try:
        logger.info(f"Создание нового вида деятельности: {data.name}, parent_id={data.parent_id}")

        level = 0
        if data.parent_id is not None:
            parent = await session.get(ActivityModel, data.parent_id)
            if not parent:
                logger.warning(f"Указанный родительский вид деятельности ID={data.parent_id} не найден")
                raise HTTPException(status_code=404, detail="Родительский вид деятельности не найден")
            if parent.level >= 2:
                logger.warning(f"Нельзя создать потомка для вида деятельности с уровнем 2")
                raise HTTPException(status_code=400, detail="Нельзя создать потомка для уровня 2")
            level = parent.level + 1

        new_activity = ActivityModel(
            name=data.name,
            parent_id=data.parent_id,
            level=level
        )
        session.add(new_activity)
        await session.commit()
        await session.refresh(new_activity)

        logger.info(f"Вид деятельности создан с ID={new_activity.id}")
        return new_activity

    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при создании вида деятельности: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/{activity_id}", response_model=ActivityWithChildren)
async def get_activity(activity_id: int, session: AsyncSession = get_session()):
    """
    Получить вид деятельности по ID, включая дочерние элементы.
    """
    try:
        logger.info(f"Запрошен вид деятельности ID={activity_id}")

        activity = await session.get(ActivityModel, activity_id)
        if not activity:
            logger.warning(f"Вид деятельности ID={activity_id} не найден")
            raise HTTPException(status_code=404, detail="Вид деятельности не найден")

        async def build_tree(activity: ActivityModel, current_level: int = activity.level,
                             max_level: int = 2) -> ActivityWithChildren:
            """Рекурсивно строит дерево активности."""
            children_list = []
            if current_level < max_level:
                result = await session.execute(select(ActivityModel).where(ActivityModel.parent_id == activity.id))
                children = result.scalars().all()
                for child in children:
                    children_list.append(await build_tree(child, current_level + 1, max_level))

            return ActivityWithChildren(
                id=activity.id,
                name=activity.name,
                parent_id=activity.parent_id,
                level=current_level,
                children=children_list
            )

        tree = await build_tree(activity)
        logger.debug(f"Вид деятельности с дочерними элементами сформирован: ID={activity.id}")
        return tree

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении вида деятельности {activity_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
