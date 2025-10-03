# Purpose: Application configuration settings.
# Context: Pydantic Settings for environment variables.
# Requirements: Database URLs, security keys, Telegram Bot token.

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./family_habits.db"
    database_url_sync: str = "sqlite:///./family_habits.db"
    
    # Telegram Bot
    telegram_bot_token: str = "demo_token_for_testing"
    webapp_url: str = "https://example.com"
    
    # FastAPI
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # Security
    secret_key: str = "demo-secret-key-change-in-production"
    admin_user_ids: str = "123456789,987654321"
    
    # Logging
    log_level: str = "INFO"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Subscription
    sub_price_rub: int = 299
    
    # Environment
    environment: str = "development"
    
    @property
    def TELEGRAM_BOT_TOKEN(self) -> str:
        return self.telegram_bot_token
    
    @property
    def WEBAPP_URL(self) -> str:
        return self.webapp_url
    
    @property
    def ADMIN_USER_IDS(self) -> list[int]:
        """Parse comma-separated admin IDs into list of integers."""
        return [int(x.strip()) for x in self.admin_user_ids.split(",") if x.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()