from uuid import uuid4
from httpx import AsyncClient

from src.core.models.user import User
from tests.utils.constants import NEW_TASK


async def test_create_task(admin_client: AsyncClient):
    response = await admin_client.post("/tasks", json=NEW_TASK)
    
    assert response.status_code == 201
    assert response.json() is not None and response.json()["name"] == NEW_TASK["name"]

async def test_create_with_invalid_executors(admin_client: AsyncClient):
    data = NEW_TASK.copy()
    data["executors"] = [str(uuid4()), str(uuid4())]
    response = await admin_client.post("/tasks", json=data)

    assert response.status_code == 404
    assert "detail" in response.json() and response.json()["detail"] == "Executor not found"

async def test_create_task_by_executor(admin_client: AsyncClient, manager_user: User):
    data = NEW_TASK.copy()
    data["executors"] = [manager_user.id]
    response = await admin_client.post("/tasks", json=NEW_TASK)
    
    assert response.status_code == 201
    assert response.json() is not None and response.json()["name"] == NEW_TASK["name"]

async def test_create_task_invalid_data(admin_client: AsyncClient):
    data = {"name": ""}
    response = await admin_client.post("/tasks", data=data)

    assert response.status_code == 422

async def test_create_task_unauthorized(client: AsyncClient):
    response = await client.post("/tasks", data=NEW_TASK)

    assert response.status_code == 401
    assert "detail" in response.json() and response.json()["detail"] == "Not authenticated"
