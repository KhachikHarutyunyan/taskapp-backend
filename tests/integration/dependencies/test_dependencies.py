from unittest.mock import AsyncMock, MagicMock

from src.api.auth.service import AuthService
from src.api.dependencies import (
    get_auth_service,
    get_auth_uow,
    get_task_service,
    get_task_uow,
)
from src.api.task.service import TaskService
from src.api.units_of_work import AuthUnitOfWork, TaskUnitOfWork


async def test_get_auth_uow():
    mock_session = AsyncMock()

    uow = await get_auth_uow(mock_session)

    assert isinstance(uow, AuthUnitOfWork)
    assert uow.session == mock_session
    assert hasattr(uow, "user_repository")


async def test_get_auth_service():
    mock_uow = MagicMock(spec=AuthUnitOfWork)
    service = await get_auth_service(mock_uow)

    assert isinstance(service, AuthService)
    assert service.uow == mock_uow


async def test_get_task_uow():
    mock_session = AsyncMock()
    uow = await get_task_uow(mock_session)

    assert isinstance(uow, TaskUnitOfWork)
    assert uow.session == mock_session
    assert hasattr(uow, "task_repository")


async def test_get_task_service():
    mock_uow = MagicMock(spec=TaskUnitOfWork)
    service = await get_task_service(mock_uow)

    assert isinstance(service, TaskService)
    assert service.uow == mock_uow
