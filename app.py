import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, Request, Response

from logging_conf import configure_logging, request_id_ctx
from settings import get_settings

settings = get_settings()
configure_logging(level=settings.log_level)

app = FastAPI(title="Todo Integration ML", version="0.1.0")


@app.middleware("http")
async def request_context_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Attach request_id to context and propagate it via response header."""
    rid = request.headers.get("x-request-id", str(uuid.uuid4()))
    token = request_id_ctx.set(rid)
    try:
        response = await call_next(request)
    finally:
        request_id_ctx.reset(token)
    response.headers["x-request-id"] = rid
    return response


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, Any]:
    return {"status": "ready"}
