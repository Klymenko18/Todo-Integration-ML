from typing import Any

from celery_app import celery_app
from file_utils import atomic_write_csv
from http_client import fetch_json
from settings import get_settings

_settings = get_settings()


@celery_app.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def fetch_users_to_csv() -> str:
    """Fetch users and write minimal CSV (id, name, email)."""
    url = "https://jsonplaceholder.typicode.com/users"
    data: list[dict[str, Any]] = fetch_json(url)
    rows = [(str(r.get("id", "")), str(r.get("name", "")), str(r.get("email", ""))) for r in data]
    out = f"{_settings.data_dir.rstrip('/')}/users.csv"
    atomic_write_csv(out, rows, header=["id", "name", "email"])
    return out
