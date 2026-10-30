from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.utils.constants import PASSWORD_NOT_STRONG_MSG
from src.core.models import User
from tests.utils.constants import BASE_PASSWORD, MANAGER_USER, REGISTER_USER


async def test_register_success(async_session: AsyncSession, client: AsyncClient):
    response = await client.post("/auth/register", json=REGISTER_USER)

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data

    result = await async_session.execute(
        select(User).where(User.email == REGISTER_USER["email"])
    )
    user = result.scalar_one()
    assert user.email == REGISTER_USER["email"]


async def test_register_email_already_exists(client: AsyncClient):
    response = await client.post("/auth/register", json=REGISTER_USER)

    assert response.status_code == 201
    assert "access_token" in response.json()

    response = await client.post("/auth/register", json=REGISTER_USER)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exist please choose another one"


async def test_register_passwords_missmatch(client: AsyncClient):
    payload = {**REGISTER_USER, "confirm_password": "NotMatchPass"}
    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords don't match"


async def test_register_password_not_strong(client: AsyncClient):
    payload = {
        **REGISTER_USER,
        "email": "weak@mailbox.com",
        "password": "notstrong",
        "confirm_password": "notstrong",
    }
    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == PASSWORD_NOT_STRONG_MSG


async def test_login_user(client: AsyncClient, manager_user: User):
    data = {"username": MANAGER_USER["email"], "password": BASE_PASSWORD}
    response = await client.post("/auth/login", data=data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.cookies


async def test_login_invalid_email(client: AsyncClient):
    data = {"username": "missing@mailbox.com", "password": BASE_PASSWORD}
    response = await client.post("/auth/login", data=data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"


async def test_login_wrong_password(client: AsyncClient, manager_user: User):
    data = {"username": MANAGER_USER["email"], "password": "WrongPass1!"}
    response = await client.post("/auth/login", data=data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"


async def test_logout_user(manager_client: AsyncClient):
    assert manager_client.cookies["refresh_token"] is not None

    response = await manager_client.post("/auth/logout")
    assert response.json()["detail"] == "Successfully logged out"
