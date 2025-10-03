# Purpose: Конфигурация приложения через переменные окружения.
# Context: Centralized settings using pydantic-settings for type safety and validation.
# Requirements: Load all environment variables, validate critical ones, provide defaults.

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    database_url: str = Field(..., description="PostgreSQL connection URL for async operations")
    database_url_sync: str = Field(..., description="PostgreSQL connection URL for sync operations (Alembic)")
    
    # Telegram Bot
    bot_token: str = Field(..., description="Telegram Bot API token")
    webapp_url: str = Field(..., description="URL of the Telegram MiniApp")
    
    # FastAPI
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    api_workers: int = Field(default=1, description="Number of API workers")
    
    # Security
    secret_key: str = Field(..., description="Secret key for signing")
    admin_ids: str = Field(default="", description="Comma-separated list of admin Telegram IDs")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # Subscription
    sub_price_rub: int = Field(default=299, description="Pro subscription price in rubles")
    
    # Environment
    environment: str = Field(default="development", description="Environment name")
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Список ID администраторов."""
        if not self.admin_ids:
            return []
        return [int(id_.strip()) for id_ in self.admin_ids.split(",") if id_.strip()]
    
    @property
    def is_production(self) -> bool:
        """Проверка продакшн окружения."""
        return self.environment.lower() == "production"


# Глобальный экземпляр настроек
settings = Settings()