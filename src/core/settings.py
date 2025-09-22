from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"

    data_dir: str = "./data"
    model_path: str = "./data/model.joblib"

    redis_url: str = Field(
        default="redis://redis:6379/0",
        validation_alias=AliasChoices("REDIS_URL", "redis_url"),
    )
    celery_broker_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CELERY_BROKER_URL", "celery_broker_url"),
    )
    celery_result_backend: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "CELERY_RESULT_BACKEND", "CELERY_BACKEND", "celery_result_backend", "celery_backend"
        ),
    )

    http_timeout: float = 5.0
    http_max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    def __init__(self, **data):
        super().__init__(**data)
        if self.celery_broker_url is None:
            object.__setattr__(self, "celery_broker_url", self.redis_url)
        if self.celery_result_backend is None:
            default_backend = (
                self.redis_url.replace("/0", "/1")
                if self.redis_url.endswith("/0")
                else self.redis_url
            )
            object.__setattr__(self, "celery_result_backend", default_backend)


@lru_cache
def get_settings() -> Settings:
    return Settings()
