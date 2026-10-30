from httpx import AsyncClient

from src.core.models.user import User
from tests.utils.constants import NEW_TASK


async def test_create_task(admin_client: AsyncClient):
    response = await admin_client.post("/tasks", json=NEW_TASK)

    assert response.status_code == 201
    body = response.json()
    assert body is not None
    assert body["name"] == NEW_TASK["name"]
    assert body["description"] == NEW_TASK["description"]


async def test_create_task_validation_error(admin_client: AsyncClient):
    response = await admin_client.post("/tasks", json={"name": "ab"})

    assert response.status_code == 422


async def test_create_task_sets_author(admin_client: AsyncClient, admin_user: User):
    response = await admin_client.post("/tasks", json=NEW_TASK)

    assert response.status_code == 201
    assert response.json()["author_id"] == str(admin_user.id)
    assert response.json()["name"] == NEW_TASK["name"]


async def test_create_task_invalid_data(admin_client: AsyncClient):
    response = await admin_client.post("/tasks", json={"name": ""})

    assert response.status_code == 422


async def test_create_task_unauthorized(client: AsyncClient):
    response = await client.post("/tasks", json=NEW_TASK)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
