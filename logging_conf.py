import logging
import sys
from contextvars import ContextVar

# Context var to store request_id (set in middleware later)
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True


def configure_logging(level: str = "INFO") -> None:
    """Configure structured logging with request_id support."""
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
    root.setLevel(level)
    root.addHandler(handler)
    root.addFilter(RequestIdFilter())
