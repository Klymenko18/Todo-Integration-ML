import threading
import uuid
from datetime import UTC, datetime

from todo_models import TaskCreate, TaskResponse, TaskUpdate


class InMemoryTaskService:
    """Thread-safe in-memory storage for tasks."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._data: dict[str, TaskResponse] = {}

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        is_done: bool | None = None,
    ) -> tuple[list[TaskResponse], int]:
        with self._lock:
            values = list(self._data.values())
            if is_done is not None:
                values = [t for t in values if t.is_done == is_done]
            total = len(values)
            return values[offset : offset + limit], total

    def create(self, payload: TaskCreate) -> TaskResponse:
        now = datetime.now(UTC)
        tid = str(uuid.uuid4())
        item = TaskResponse(
            id=tid,
            title=payload.title,
            description=payload.description,
            is_done=payload.is_done,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._data[tid] = item
        return item

    def update(self, task_id: str, payload: TaskUpdate) -> TaskResponse:
        with self._lock:
            if task_id not in self._data:
                raise KeyError(task_id)
            cur = self._data[task_id]
            new = cur.model_copy(
                update={
                    "title": payload.title if payload.title is not None else cur.title,
                    "description": (
                        payload.description if payload.description is not None else cur.description
                    ),
                    "is_done": payload.is_done if payload.is_done is not None else cur.is_done,
                    "updated_at": datetime.now(UTC),
                }
            )
            self._data[task_id] = new
            return new

    def delete(self, task_id: str) -> None:
        with self._lock:
            # idempotent delete
            self._data.pop(task_id, None)
