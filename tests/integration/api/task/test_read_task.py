from typing import List
from uuid import uuid4

from httpx import AsyncClient

from src.core.models import Task
from tests.utils.constants import TASKS_LIST


async def test_get_task(admin_client: AsyncClient, new_task: Task):
    response = await admin_client.get(f"/tasks/{new_task.id}")

    assert response.status_code == 200
    assert response.json()["name"] == new_task.name


async def test_get_not_found(admin_client: AsyncClient):
    response = await admin_client.get(f"/tasks/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Resource not found"


async def test_get_unauthorized(client: AsyncClient, new_task: Task):
    response = await client.get(f"/tasks/{new_task.id}")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_get_all_tasks(admin_client: AsyncClient, task_list: List[Task]):
    response = await admin_client.get("/tasks")

    assert response.status_code == 200
    assert response.json() is not None
    assert len(response.json()) == len(TASKS_LIST)


async def test_get_all_unauthorized(client: AsyncClient, task_list: List[Task]):
    response = await client.get("/tasks")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
