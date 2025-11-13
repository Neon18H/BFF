from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class TaskStatus(str, Enum):
    sin_iniciar = "sin_iniciar"
    en_proceso = "en_proceso"
    finalizado = "finalizado"


class TaskBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    title: str
    description: Optional[str] = None
    status: TaskStatus
    labels: List[str] = []
    due_date: Optional[datetime] = Field(alias="dueDate", default=None)
    add_to_calendar: bool = Field(alias="addToCalendar", default=False)
    order: float


class Task(TaskBase):
    id: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class TaskCreate(TaskBase):
    created_at: Optional[datetime] = Field(alias="createdAt", default=None)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    labels: Optional[List[str]] = None
    due_date: Optional[datetime] = Field(alias="dueDate", default=None)
    add_to_calendar: Optional[bool] = Field(alias="addToCalendar", default=None)
    order: Optional[float] = None
    created_at: Optional[datetime] = Field(alias="createdAt", default=None)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)


class TaskList(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    items: List[Task]
    total: int
    page: int
    page_size: int


class TaskFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    status: Optional[TaskStatus] = None
    due_from: Optional[datetime] = Field(default=None, alias="dueFrom")
    due_to: Optional[datetime] = Field(default=None, alias="dueTo")
    q: Optional[str] = None


__all__ = [
    "Task",
    "TaskCreate",
    "TaskUpdate",
    "TaskList",
    "TaskStatus",
    "TaskFilters",
]
