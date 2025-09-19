from __future__ import annotations

from typing import Any


def make_celery(
    broker_url: str,
    backend_url: str | None = None,
    app_name: str = "app",
) -> Any:
    import importlib

    celery_mod = importlib.import_module("celery")
    Celery = celery_mod.Celery
    celery = Celery(app_name, broker=broker_url, backend=backend_url or broker_url)
    celery.conf.task_serializer = "json"
    celery.conf.result_serializer = "json"
    celery.conf.accept_content = ["json"]
    return celery


celery_app = make_celery(broker_url="redis://localhost:6379/0")
