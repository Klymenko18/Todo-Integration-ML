import threading

from src.models.todo_models import TaskCreate, TaskResponse, TaskUpdate


class InMemoryTaskService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._data: dict[int, TaskResponse] = {}
        self._counter: int = 0

    def list(self, *, is_done: bool | None = None) -> list[TaskResponse]:
        with self._lock:
            values = list(self._data.values())
            if is_done is not None:
                values = [t for t in values if t.is_done == is_done]
            return values

    def create(self, payload: TaskCreate) -> TaskResponse:
        with self._lock:
            self._counter += 1
            tid = self._counter
            item = TaskResponse(
                id=tid,
                title=payload.title,
                description=payload.description,
                is_done=payload.is_done,
            )
            self._data[tid] = item
            return item

    def update(self, task_id: int, payload: TaskUpdate) -> TaskResponse:
        with self._lock:
            if task_id not in self._data:
                raise KeyError(task_id)
            cur = self._data[task_id]
            new = TaskResponse(
                id=task_id,
                title=payload.title if payload.title is not None else cur.title,
                description=(
                    payload.description if payload.description is not None else cur.description
                ),
                is_done=payload.is_done if payload.is_done is not None else cur.is_done,
            )
            self._data[task_id] = new
            return new

    def delete(self, task_id: int) -> None:
        with self._lock:
            self._data.pop(task_id, None)
