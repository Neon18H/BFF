from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response

from app.core.security import AuthContext, get_auth_context
from app.db.supabase_client import SupabaseClient, get_supabase_client
from app.models.tasks import Task, TaskCreate, TaskFilters, TaskList, TaskStatus, TaskUpdate
from app.services.tasks_service import TasksService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_tasks_service(supabase: SupabaseClient = Depends(get_supabase_client)) -> TasksService:
    return TasksService(supabase)


@router.get("", response_model=TaskList)
async def list_tasks(
    auth: AuthContext = Depends(get_auth_context),
    service: TasksService = Depends(get_tasks_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[TaskStatus] = Query(default=None),
    due_from: Optional[datetime] = Query(default=None, alias="dueFrom"),
    due_to: Optional[datetime] = Query(default=None, alias="dueTo"),
    q: Optional[str] = Query(default=None),
) -> TaskList:
    filters = TaskFilters(status=status, due_from=due_from, due_to=due_to, q=q)
    return await service.list_tasks(
        auth.access_token,
        page=page,
        page_size=page_size,
        filters=filters,
    )


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    auth: AuthContext = Depends(get_auth_context),
    service: TasksService = Depends(get_tasks_service),
) -> Task:
    return await service.get_task(auth.access_token, task_id)


@router.post("", response_model=Task, status_code=201)
async def create_task(
    payload: TaskCreate,
    auth: AuthContext = Depends(get_auth_context),
    service: TasksService = Depends(get_tasks_service),
) -> Task:
    return await service.create_task(auth.access_token, payload)


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    auth: AuthContext = Depends(get_auth_context),
    service: TasksService = Depends(get_tasks_service),
) -> Task:
    return await service.update_task(auth.access_token, task_id, payload)


@router.delete("/{task_id}", status_code=204, response_class=Response)
async def delete_task(
    task_id: str,
    auth: AuthContext = Depends(get_auth_context),
    service: TasksService = Depends(get_tasks_service),
) -> Response:
    await service.delete_task(auth.access_token, task_id)
    return Response(status_code=204)


@router.post("/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: str,
    auth: AuthContext = Depends(get_auth_context),
    service: TasksService = Depends(get_tasks_service),
) -> Task:
    return await service.complete_task(auth.access_token, task_id)
