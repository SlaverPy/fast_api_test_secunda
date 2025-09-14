from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware для проверки статического API ключа.

    Проверяет заголовок 'x-api-key' во всех входящих запросах.
    Если ключ неверный, возвращает HTTP 401 Unauthorized и логирует попытку доступа.
    """

    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("x-api-key")
        if api_key != settings.API_KEY:
            logger.warning(f"Попытка доступа с неверным API ключом: {api_key}")
            raise HTTPException(status_code=401, detail="Неверный API ключ")
        logger.info(f"Доступ разрешён для API ключа: {api_key}")
        response = await call_next(request)
        return response
