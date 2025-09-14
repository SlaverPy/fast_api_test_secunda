from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from .config import settings

engine = create_engine(
    str(settings.DATABASE.DATABASE_URL),
    poolclass=QueuePool,
    pool_size=settings.DATABASE.DB_POOL_SIZE,
    max_overflow=settings.DATABASE.DB_MAX_OVERFLOW,
    pool_recycle=settings.DATABASE.DB_POOL_RECYCLE,
    pool_timeout=settings.DATABASE.DB_POOL_TIMEOUT,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Генератор сессий БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
