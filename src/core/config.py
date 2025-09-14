# config.py
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения."""

    API_KEY: str = Field(..., description="Статический API ключ для аутентификации")

    # Database settings
    DB_HOST: str = Field("localhost", description="Хост базы данных")
    DB_PORT: int = Field(5432, description="Порт базы данных")
    DB_NAME: str = Field("your_database", description="Название базы данных")
    DB_USER: str = Field("postgres", description="Пользователь базы данных")
    DB_PASSWORD: str = Field("postgres", description="Пароль базы данных")

    # Database pool settings
    DB_POOL_SIZE: int = Field(20, description="Размер пула соединений")
    DB_MAX_OVERFLOW: int = Field(10, description="Максимальное переполнение пула")
    DB_POOL_RECYCLE: int = Field(3600, description="Время пересоздания соединения (сек)")
    DB_POOL_TIMEOUT: int = Field(30, description="Таймаут пула (сек)")

    # Logging settings
    DEBUG: bool = Field(False, description="Режим отладки (DEBUG=True → уровень DEBUG, иначе INFO)")
    LOG_MAX_FILE_SIZE: int = Field(10 * 1024 * 1024, description="Максимальный размер файла лога (байты)")
    LOG_BACKUP_COUNT: int = Field(5, description="Количество backup файлов")

    @property
    def LOG_LEVEL(self) -> str:
        return "DEBUG" if self.DEBUG else "INFO"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


settings = Settings()
