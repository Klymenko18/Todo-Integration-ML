from __future__ import annotations

from celery import Celery

from src.core.settings import get_settings

settings = get_settings()
redis_url = getattr(settings, "redis_url", "redis://redis:6379/1")

celery_app = Celery(
    "todo_integration_ml",
    broker=redis_url,
    backend=redis_url,
    include=[
        "src.workers.tasks.task_fetch_users",
        "src.workers.tasks.task_train_model",
    ],
)

celery_app.conf.update(
    task_default_queue="default",
    timezone="UTC",
    enable_utc=True,
)

__all__ = ["celery_app"]
