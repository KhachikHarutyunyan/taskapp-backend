from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest
from fastapi import Request
from httpx import ASGITransport, AsyncClient

from src.api.auth.service import AuthService
from src.api.dependencies import (
    get_auth_service,
    get_current_user,
    get_user_id_from_refresh_token,
)
from src.config.settings import settings
from src.core.models import User


@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    request.cookies = {}
    return request


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.user_repository = AsyncMock()
    return uow


@pytest.fixture
def mock_get_current_user():
    async def get_current_user_mock(request: Request = None):
        return MagicMock(spec=User, id=1, email="test@example.com")

    return get_current_user_mock


@pytest.fixture
def mock_user_id_from_refresh_token():
    async def user_id_from_refresh_token_mock(request: Request = None):
        return "user_id_123"

    return user_id_from_refresh_token_mock


@pytest.fixture
async def auth_client(
    test_app,
    mock_get_current_user,
    mock_user_id_from_refresh_token,
):
    test_app.dependency_overrides[get_current_user] = mock_get_current_user
    test_app.dependency_overrides[get_user_id_from_refresh_token] = (
        mock_user_id_from_refresh_token
    )

    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url=f"http://test{settings.API_VERSION}",
        follow_redirects=True,
    ) as client:
        client.cookies.set("refresh_token", "test_refresh_token")
        client.test_app = test_app
        yield client

    test_app.dependency_overrides.clear()


@pytest.fixture
def mock_auth_service():
    mock_service = create_autospec(AuthService)
    mock_service.register = AsyncMock()
    mock_service.login = AsyncMock()
    mock_service.update_provider = AsyncMock()
    return mock_service


@pytest.fixture
def mocked_app_auth_service(test_app, mock_auth_service):
    test_app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    return test_app


@pytest.fixture
async def mocked_auth_client(mocked_app_auth_service):
    async with AsyncClient(
        transport=ASGITransport(app=mocked_app_auth_service),
        base_url=f"http://test{settings.API_VERSION}",
    ) as client:
        yield client
