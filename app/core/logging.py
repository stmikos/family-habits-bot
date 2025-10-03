# Purpose: Logging configuration.
# Context: Structured logging with loguru.
# Requirements: Consistent logging across all modules.

import sys
from loguru import logger


def setup_logging(level: str = "INFO"):
    """Setup application logging."""
    logger.remove()  # Remove default handler
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file handler for errors
    logger.add(
        "logs/errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )


def get_logger(name: str):
    """Get logger instance for module."""
    return logger.bind(name=name)