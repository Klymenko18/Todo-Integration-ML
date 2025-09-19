from fastapi import APIRouter, HTTPException, status

from todo_models import Page, TaskCreate, TaskResponse, TaskUpdate
from todo_service import InMemoryTaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])
_service = InMemoryTaskService()


@router.get("", response_model=Page[TaskResponse])
def list_tasks(limit: int = 50, offset: int = 0, is_done: bool | None = None) -> Page[TaskResponse]:
    items, total = _service.list(limit=limit, offset=offset, is_done=is_done)
    return Page[TaskResponse](items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> TaskResponse:
    return _service.create(payload)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    try:
        return _service.update(task_id, payload)
    except KeyError as _err:
        raise HTTPException(status_code=404, detail="Task not found") from None


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str) -> None:
    _service.delete(task_id)
    return
