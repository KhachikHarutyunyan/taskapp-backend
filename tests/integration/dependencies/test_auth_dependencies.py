from uuid import uuid4

import pytest

from src.api.dependencies import get_current_user, get_user_id_from_refresh_token
from src.api.exceptions import UnauthorizedException
from src.config.security import create_tokens


async def test_get_current_user_valid(mock_request, mock_uow, mocker):
    mock_request.cookies = {"refresh_token": "valid_refresh_token"}
    token = "valid_access_token"

    mocker.patch(
        "src.api.dependencies.get_token_payload",
        return_value={
            "payload": {"sub": "user_id_123"},
            "is_expire": False,
        },
    )

    mock_user = mocker.MagicMock()
    mock_uow.user_repository.get.return_value = mock_user

    result = await get_current_user(mock_request, token, mock_uow)

    assert result == mock_user
    mock_uow.user_repository.get.assert_awaited_once_with("user_id_123")


async def test_get_current_user_missing_token(mock_request, mock_uow):
    with pytest.raises(UnauthorizedException) as exc:
        await get_current_user(mock_request, None, mock_uow)

    assert exc.value.detail == "Not authenticated"


async def test_get_current_user_missing_refresh_token(mock_request, mock_uow, mocker):
    mock_request.cookies = {}
    token = "valid_access_token"

    mocker.patch(
        "src.api.dependencies.get_token_payload",
        return_value={
            "payload": {"sub": "user_id_123"},
            "is_expire": False,
        },
    )

    with pytest.raises(UnauthorizedException) as exc:
        await get_current_user(mock_request, token, mock_uow)

    assert exc.value.detail == "Not authorized"


async def test_get_current_user_expired_access_token(mock_request, mock_uow, mocker):
    mock_request.cookies = {"refresh_token": "valid_refresh_token"}
    token = "expired_access_token"

    mocker.patch(
        "src.api.dependencies.get_token_payload",
        return_value={
            "payload": {"sub": "user_id_123"},
            "is_expire": True,
        },
    )

    with pytest.raises(UnauthorizedException) as exc:
        await get_current_user(mock_request, token, mock_uow)

    assert exc.value.detail == "Not authorized"


async def test_get_current_user_invalid_access_token(mock_request, mock_uow, mocker):
    mock_request.cookies = {"refresh_token": "valid_refresh_token"}
    token = "invalid_access_token"

    mocker.patch(
        "src.api.dependencies.get_token_payload",
        return_value={
            "payload": None,
            "is_expire": True,
        },
    )
    with pytest.raises(UnauthorizedException) as exc:
        await get_current_user(mock_request, token, mock_uow)

    assert "Not authorized" in exc.value.detail


async def test_get_current_user_not_found_user(mock_request, mock_uow, mocker):
    mock_request.cookies = {"refresh_token": "valid_refresh_token"}
    token = "valid_access_token"

    mocker.patch(
        "src.api.dependencies.get_token_payload",
        return_value={
            "payload": {"sub": "non_existent_user_id"},
            "is_expire": False,
        },
    )

    mock_uow.user_repository.get.return_value = None
    with pytest.raises(UnauthorizedException) as exc:
        await get_current_user(mock_request, token, mock_uow)
    assert "Not authorized" in exc.value.detail


async def test_get_current_user_missing_sub_claim(mock_request, mock_uow, mocker):
    mock_request.cookies = {"refresh_token": "valid_refresh_token"}
    token = "invalid_access_token"

    mocker.patch(
        "src.api.dependencies.get_token_payload",
        return_value={
            "payload": {},
            "is_expire": False,
        },
    )
    mock_uow.user_repository.get.return_value = None

    with pytest.raises(UnauthorizedException) as exc:
        await get_current_user(mock_request, token, mock_uow)
    assert "Not authorized" in exc.value.detail


async def test_user_id_from_refresh_token(mock_request):
    user_id = uuid4()
    _, refresh_token = create_tokens(user_id)
    mock_request.cookies = {"refresh_token": refresh_token}

    result = await get_user_id_from_refresh_token(mock_request, token=None)

    assert result == str(user_id)


async def test_user_id_from_refresh_token_missing(mock_request):
    mock_request.cookies = {}

    with pytest.raises(UnauthorizedException) as exc:
        await get_user_id_from_refresh_token(mock_request, token=None)

    assert "Refresh token is missing" in exc.value.detail


async def test_user_id_from_refresh_token_invalid(mock_request):
    mock_request.cookies = {"refresh_token": "invalid_refresh_token"}

    with pytest.raises(UnauthorizedException) as exc:
        await get_user_id_from_refresh_token(mock_request, token=None)

    assert "Invalid refresh token" in exc.value.detail
