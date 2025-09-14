# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import async_scoped_session
from asyncio import current_task
from src.core.config import settings

ASYNC_DATABASE_URL = str(settings.DATABASE_URL).replace(
    "postgresql://", "postgresql+asyncpg://"
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    echo=settings.DEBUG,
    connect_args={
        "ssl": "require" if getattr(settings, 'PRODUCTION', False) else None
    }
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

AsyncScopedSession = async_scoped_session(
    AsyncSessionLocal,
    scopefunc=current_task
)


async def get_session() -> AsyncSession:
    """
    Асинхронная сессия БД для FastAPI через Depends.
    Использует scoped session для автоматического управления жизненным циклом.
    """
    session = AsyncScopedSession()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()