from __future__ import annotations

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=10_000)
    is_done: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=10_000)
    is_done: bool | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    is_done: bool
