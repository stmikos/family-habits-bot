# Purpose: Настройка логирования через loguru.
# Context: Centralized logging configuration with structured logs for business events.
# Requirements: INFO for business events, WARNING for edge cases, ERROR for exceptions.

import sys
from loguru import logger
from app.core.config import settings


def setup_logging() -> None:
    """Настройка системы логирования."""
    
    # Удаляем стандартный handler
    logger.remove()
    
    # Настройка формата логов
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File handler для продакшна
    if settings.is_production:
        logger.add(
            "logs/app.log",
            format=log_format,
            level=settings.log_level,
            rotation="100 MB",
            retention="30 days",
            compression="gz",
            backtrace=True,
            diagnose=True
        )
    
    logger.info(f"Logging configured with level: {settings.log_level}")


def get_logger(name: str = None):
    """Получить logger для модуля."""
    return logger.bind(module=name) if name else logger