from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def _record_factory_with_request_id(
    base_factory: Callable[..., logging.LogRecord],
) -> Callable[..., logging.LogRecord]:
    def factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
        record = base_factory(*args, **kwargs)
        if not hasattr(record, "request_id"):
            record.request_id = request_id_ctx.get()
        return record

    return factory


def configure_logging(level: str = "INFO") -> None:
    logging.setLogRecordFactory(_record_factory_with_request_id(logging.getLogRecordFactory()))
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt=(
            '{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s",'
            '"msg":"%(message)s","request_id":"%(request_id)s"}'
        ),
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(handler)
    for noisy in ("uvicorn.error", "uvicorn.access", "multipart", "python_multipart", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
