from __future__ import annotations

from celery import Celery
from settings import get_settings

s = get_settings()

# ЯВНО підключаємо модуль(і) із задачами
# якщо у тебе інша назва файла з задачами — додай/заміни тут
celery_app = Celery(
    "todo_integration_ml",
    broker=s.celery_broker_url,
    backend=s.celery_result_backend,
    include=["task_fetch_users"],
)

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.task_default_queue = "default"
