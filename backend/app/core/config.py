from pydantic_settings import BaseSettings
from typing import Optional, List
import os
import secrets
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = "AI Business Development Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_bd_platform",
    )
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT & Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI/LLM
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    AI_MODEL: str = "gpt-4"

    # Temporal
    TEMPORAL_HOST: str = os.getenv("TEMPORAL_HOST", "localhost:7233")

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    def __init__(self, **data):
        """Initialize settings and validate required fields."""
        super().__init__(**data)

        # Generate random JWT secret for development if not provided
        if not self.JWT_SECRET_KEY:
            if not self.DEBUG:
                raise ValueError(
                    "JWT_SECRET_KEY must be set in production! Set the JWT_SECRET_KEY environment variable."
                )
            # Generate a secure random key for development
            self.JWT_SECRET_KEY = secrets.token_urlsafe(32)
            logger.warning(
                "JWT_SECRET_KEY not set. Generated random key for development. "
                "DO NOT USE IN PRODUCTION!"
            )

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.DEBUG:
            return ["*"]
        return self.CORS_ORIGINS

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
