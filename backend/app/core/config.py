from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed backend settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Kachalka API"
    app_env: str = "development"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+asyncpg://kachalka:kachalka_dev_password@localhost:5432/kachalka"
    )
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    openai_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Create Settings once and reuse the same instance."""

    return Settings()


settings = get_settings()
