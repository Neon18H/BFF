from __future__ import annotations

from typing import Dict, Optional

from app.core.errors import AppError
from app.db.supabase_client import SupabaseClient
from app.models.tasks import Task, TaskCreate, TaskFilters, TaskList, TaskStatus, TaskUpdate


class TasksService:
    def __init__(self, supabase: SupabaseClient):
        self._supabase = supabase

    @staticmethod
    def _parse_total(headers) -> int:
        content_range = headers.get("content-range")
        if not content_range:
            return 0
        try:
            _, total = content_range.split("/")
            return int(total)
        except ValueError:
            return 0

    def _build_filters(self, filters: TaskFilters | None) -> Dict[str, str]:
        params: Dict[str, str] = {}
        if not filters:
            return params
        if filters.status:
            params["status"] = f"eq.{filters.status.value}"
        range_parts = []
        if filters.due_from:
            range_parts.append(f"due_date.gte.{filters.due_from.isoformat()}")
        if filters.due_to:
            range_parts.append(f"due_date.lte.{filters.due_to.isoformat()}")
        if range_parts:
            params["and"] = f"({','.join(range_parts)})"
        if filters.q:
            params["or"] = f"(title.ilike.*{filters.q}*,description.ilike.*{filters.q}*)"
        return params

    async def list_tasks(
        self,
        access_token: str,
        *,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[TaskFilters] = None,
    ) -> TaskList:
        start = (page - 1) * page_size
        end = start + page_size - 1
        params: Dict[str, str] = {"select": "*", "order": "order"}
        params.update(self._build_filters(filters))
        headers = {"Range": f"{start}-{end}", "Prefer": "count=exact"}
        response = await self._supabase.rest_request(
            "GET", "tasks", access_token, params=params, headers=headers
        )
        data = response.data
        if not isinstance(data, list):
            raise AppError("Invalid response from Supabase", code="supabase_error", status_code=502)
        total = self._parse_total(response.headers)
        return TaskList(
            items=[Task.model_validate(i) for i in data],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_task(self, access_token: str, task_id: str) -> Task:
        response = await self._supabase.rest_request(
            "GET",
            "tasks",
            access_token,
            params={"select": "*", "id": f"eq.{task_id}"},
            headers={"Range": "0-0"},
        )
        data = response.data
        if isinstance(data, list) and data:
            return Task.model_validate(data[0])
        raise AppError("Task not found", code="not_found", status_code=404)

    async def create_task(self, access_token: str, payload: TaskCreate) -> Task:
        response = await self._supabase.rest_request(
            "POST",
            "tasks",
            access_token,
            json=[payload.model_dump(by_alias=False, exclude_none=True)],  #PARCHE:1
            headers={"Prefer": "return=representation"},
        )
        data = response.data
        if isinstance(data, list) and data:
            return Task.model_validate(data[0])
        raise AppError("Unable to create task", code="supabase_error", status_code=502)

    async def update_task(self, access_token: str, task_id: str, payload: TaskUpdate) -> Task:
        response = await self._supabase.rest_request(
            "PATCH",
            f"tasks?id=eq.{task_id}",
            access_token,
            json=payload.model_dump(exclude_none=True, by_alias=False),
            headers={"Prefer": "return=representation"},
        )
        data = response.data
        if isinstance(data, list) and data:
            return Task.model_validate(data[0])
        raise AppError("Task not found", code="not_found", status_code=404)

    async def delete_task(self, access_token: str, task_id: str) -> None:
        await self._supabase.rest_request("DELETE", f"tasks?id=eq.{task_id}", access_token)

    async def complete_task(self, access_token: str, task_id: str) -> Task:
        payload = TaskUpdate(status=TaskStatus.finalizado)
        return await self.update_task(access_token, task_id, payload)


__all__ = ["TasksService"]
