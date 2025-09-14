import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

from src.core.config import settings


LOG_DIR = Path.cwd() / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class LevelFileHandler(logging.Handler):
    """Handler, который пишет каждый уровень в отдельный файл с ротацией."""
    def __init__(self, base_name: Path, max_bytes: int, backup_count: int):
        super().__init__()
        self.base_name = Path(base_name)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.handlers = {}

    def get_handler(self, levelno: int) -> RotatingFileHandler:
        if levelno not in self.handlers:
            filename = f"{self.base_name}_{logging.getLevelName(levelno).lower()}.log"
            handler = RotatingFileHandler(
                filename,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding="utf-8"
            )
            handler.setLevel(levelno)
            self.handlers[levelno] = handler
        return self.handlers[levelno]

    def emit(self, record: logging.LogRecord) -> None:
        handler = self.get_handler(record.levelno)
        handler.setFormatter(self.formatter)
        handler.emit(record)


def setup_logging():
    """Настройка логирования из settings (.env)."""
    numeric_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # собираем всё, фильтруем на хендлерах

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    log_format = "%(asctime)s [%(name)s] %(levelname)s | %(funcName)s:%(lineno)d : %(message)s"
    formatter = logging.Formatter(log_format, "%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = LevelFileHandler(
        base_name=LOG_DIR / "app",
        max_bytes=settings.LOG_MAX_FILE_SIZE,
        backup_count=settings.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(numeric_level)

    logging.info(
        f"Logging setup complete. "
        f"Level: {settings.LOG_LEVEL}, Debug: {settings.DEBUG}, "
        f"Dir: {LOG_DIR}, Max size: {settings.LOG_MAX_FILE_SIZE}, "
        f"Backups: {settings.LOG_BACKUP_COUNT}"
    )
