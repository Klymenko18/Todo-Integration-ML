from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Core
    app_env: str = "dev"
    log_level: str = "INFO"

    # Paths
    data_dir: str = "./data"
    model_path: str = "./data/model.joblib"

    # Integrations
    redis_url: str = "redis://localhost:6379/0"
    celery_backend: str = "redis://localhost:6379/1"

    # HTTP
    http_timeout: float = 5.0
    http_max_retries: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance (singleton)."""
    return Settings()
