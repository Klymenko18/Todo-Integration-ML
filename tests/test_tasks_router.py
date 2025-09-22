from __future__ import annotations

from typing import Any

from fastapi import status
from pydantic import BaseModel

from src.models.todo_models import TaskCreate, TaskUpdate
from src.services.todo_service import InMemoryTaskService


def _sample_for_field(ann: Any):
    origin = getattr(ann, "__origin__", None)
    if ann is str:
        return "sample"
    if ann is int:
        return 1
    if ann is bool:
        return False
    if origin is list:
        return []
    return "x"


def _build_payload_from_model(model: type[BaseModel]) -> dict:
    data = {}
    for name, field in model.model_fields.items():
        if field.is_required():
            data[name] = _sample_for_field(field.annotation)
    return data


def test_tasks_crud_smoke(client, override_deps):
    svc = InMemoryTaskService()

    with override_deps(get_todo_service=lambda: svc):
        create_payload = _build_payload_from_model(TaskCreate)
        r = client.post("/tasks", json=create_payload)
        assert r.status_code == status.HTTP_201_CREATED
        created = r.json()
        tid = created.get("id") or 1

        r = client.get("/tasks")
        assert r.status_code == status.HTTP_200_OK
        assert isinstance(r.json(), list)

        upd_payload = {}
        for name, field in TaskUpdate.model_fields.items():
            upd_payload[name] = _sample_for_field(field.annotation)
            break

        r = client.put(f"/tasks/{tid}", json=upd_payload)
        assert r.status_code == status.HTTP_200_OK

        r = client.delete(f"/tasks/{tid}")
        assert r.status_code in (
            status.HTTP_204_NO_CONTENT,
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
        )
