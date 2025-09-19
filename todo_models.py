from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(Generic[T], BaseModel):
    items: list[T]
    total: int
    limit: int = Field(50, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=10_000)
    is_done: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=10_000)
    is_done: bool | None = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    is_done: bool
    created_at: datetime
    updated_at: datetime
