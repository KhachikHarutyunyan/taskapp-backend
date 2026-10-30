from uuid import uuid4

from httpx import AsyncClient

from src.core.models import Task


async def test_update_task(admin_client: AsyncClient, new_task: Task):
    new_data = {"name": "New Updated Name"}
    assert new_task.name != new_data["name"]

    response = await admin_client.patch(f"/tasks/{new_task.id}", json=new_data)

    assert response.status_code == 200
    assert response.json()["name"] == new_data["name"]


async def test_update_unauthorized(client: AsyncClient, new_task: Task):
    new_data = {"name": "New Updated Name"}
    response = await client.patch(f"/tasks/{new_task.id}", json=new_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_update_empty_data(admin_client: AsyncClient, new_task: Task):
    response = await admin_client.patch(f"/tasks/{new_task.id}", json={})

    assert response.status_code == 200
    assert response.json()["name"] == new_task.name


async def test_update_not_found(admin_client: AsyncClient):
    response = await admin_client.patch(f"/tasks/{uuid4()}", json={"name": "No task"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Resource not found"


async def test_delete_task(admin_client: AsyncClient, new_task: Task):
    response = await admin_client.delete(f"/tasks/{new_task.id}")
    assert response.status_code == 204

    response = await admin_client.get(f"/tasks/{new_task.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Resource not found"


async def test_delete_not_found(admin_client: AsyncClient):
    response = await admin_client.delete(f"/tasks/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Resource not found"


async def test_delete_unauthorized(client: AsyncClient, new_task: Task):
    response = await client.delete(f"/tasks/{new_task.id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
