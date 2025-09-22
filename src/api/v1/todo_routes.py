from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.core.dependencies import get_current_user, get_todo_service
from src.models.todo_models import TaskCreate, TaskResponse, TaskUpdate
from src.services.todo_service import InMemoryTaskService

router = APIRouter(
    prefix="/todos",
    tags=["Todos"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[TaskResponse])
def list_todos(
    is_done: bool | None = Query(None, description="Filter by execution status"),
    svc: InMemoryTaskService = Depends(get_todo_service),
) -> list[TaskResponse]:
    return svc.list(is_done=is_done)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    payload: TaskCreate,
    svc: InMemoryTaskService = Depends(get_todo_service),
) -> TaskResponse:
    return svc.create(payload)


@router.put("/{task_id}", response_model=TaskResponse)
def update_todo(
    task_id: int,
    payload: TaskUpdate,
    svc: InMemoryTaskService = Depends(get_todo_service),
) -> TaskResponse:
    try:
        return svc.update(task_id, payload)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    task_id: int,
    svc: InMemoryTaskService = Depends(get_todo_service),
) -> None:
    svc.delete(task_id)
    return
