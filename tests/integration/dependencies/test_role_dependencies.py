from unittest.mock import MagicMock

import pytest

from src.api.dependencies import CheckRole
from src.api.exceptions import PermissionDeniedException
from src.api.utils.constants import Roles


async def test_check_role_valid():
    mock_user = MagicMock()
    mock_user.role.name = Roles.ADMIN.value

    check_role = CheckRole(roles=[Roles.ADMIN.value])

    result = await check_role(mock_user)
    assert result == mock_user


async def test_check_role_invalid():
    mock_user = MagicMock()
    mock_user.role.name = Roles.WORKER.value

    check_role = CheckRole(roles=[Roles.ADMIN.value])

    with pytest.raises(PermissionDeniedException):
        await check_role(mock_user)
