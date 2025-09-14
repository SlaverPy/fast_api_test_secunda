from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from src.api.routers import organizations, buildings, activities
from src.core.database import engine, Base
from src.core.logging import setup_logging
from src.core.config import settings
from src.middleware import APIKeyMiddleware

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    logger.info("Starting application...")
    if settings.DEBUG:
        logger.debug("Debug mode enabled - detailed logging will be provided")

    # Create tables on startup
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

    yield

    logger.info("Shutting down application...")
    # Cleanup on shutdown


app = FastAPI(
    title="Organization Directory API",
    description="REST API для справочника организаций, зданий и видов деятельности",
    version="1.0.0",
    lifespan=lifespan
)

# Include middleware
app.add_middleware(APIKeyMiddleware)

# Include routers
app.include_router(organizations.router)
app.include_router(buildings.router)
app.include_router(activities.router)


@app.get("/")
async def root():
    """Корневой endpoint API."""
    logger.info("Root endpoint accessed")
    return {
        "message": "Organization Directory API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "healthy", "database": "connected"}