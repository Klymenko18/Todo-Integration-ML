from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from celery.result import AsyncResult
from fastapi import FastAPI, Request
from starlette.responses import Response

from src.api.v1.auth_routes import router as auth_router
from src.api.v1.predict_routes import router as predict_router
from src.api.v1.todo_routes import router as todo_router
from src.api.v1.user_routes import router as user_router
from src.core.celery_app import celery_app
from src.core.settings import get_settings
from src.logging_conf import configure_logging, request_id_ctx
from src.workers.tasks.task_fetch_users import fetch_users_to_csv

settings = get_settings()
configure_logging(level=settings.log_level)

app = FastAPI(
    title="Todo Integration ML",
    version="0.1.0",
    description="REST API для to-do та інтеграції з Celery/Redis",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(todo_router)
app.include_router(predict_router)


@app.middleware("http")
async def request_context_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    rid = request.headers.get("x-request-id", str(uuid.uuid4()))
    token = request_id_ctx.set(rid)
    try:
        response = await call_next(request)
    finally:
        request_id_ctx.reset(token)
    response.headers["x-request-id"] = rid
    return response


@app.get("/health", tags=["Service"], summary="Healthcheck endpoint")
async def health() -> dict[str, Any]:
    return {"status": "ok"}


@app.get("/ready", tags=["Service"], summary="Readiness endpoint")
async def ready() -> dict[str, Any]:
    return {"status": "ready"}


@app.post("/tasks/fetch-users", tags=["Celery Tasks"], summary="Fetch users and save to CSV")
def trigger_fetch_users() -> dict[str, str]:
    task = fetch_users_to_csv.delay()
    return {"task_id": task.id}


@app.get("/tasks/status/{task_id}", tags=["Celery Tasks"], summary="Check Celery task status")
def task_status(task_id: str) -> dict[str, str]:
    res = AsyncResult(task_id, app=celery_app)
    return {"task_id": task_id, "state": str(res.state)}
