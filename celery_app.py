from typing import Any

# mypy: disable-error-code=import-not-found
from celery import Celery  # type: ignore[import-not-found]

from settings import get_settings

_settings = get_settings()

celery_app: Any = Celery(
    "todo_integration_ml",
    broker=_settings.redis_url,
    backend=_settings.celery_backend,
)
celery_app.conf.task_acks_late = True
celery_app.conf.result_expires = 3600
celery_app.autodiscover_tasks(packages=["."])
