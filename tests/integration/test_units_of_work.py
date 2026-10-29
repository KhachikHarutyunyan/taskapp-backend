from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.utils.constants import Roles
from src.api.units_of_work import AuthUnitOfWork
from src.api.account.repository import UserRepository, RolesRepository

async def test_auth_uow_initialization(async_session: AsyncSession):
    uow = AuthUnitOfWork(async_session)

    assert isinstance(uow, AuthUnitOfWork)
    assert uow.session == async_session
    assert isinstance(uow.user_repository, UserRepository)
    assert isinstance(uow.role_repository, RolesRepository)
    assert uow.user_repository.session == async_session
    assert uow.role_repository.session == async_session

async def test_auth_uow_commit_rollback(async_session: AsyncSession):
    uow = AuthUnitOfWork(async_session)

    try:
        async with uow.atomic() as uow_ctx:
            assert uow_ctx.user_repository is not None
            assert uow_ctx.role_repository is not None

            role = await uow_ctx.role_repository.get_by_name(Roles.WORKER.value)
            user = await uow_ctx.user_repository.create(
                name="test", 
                email="test@example.com", 
                password="hashed_password",
                role_id=role.id
            )
            assert user.id is not None

            # Generate error for testing rollback works
            raise ValueError("Test Error")
    except ValueError:
        pass

    # checking changes not saved
    result = await async_session.execute(text("SELECT * FROM users"))
    users = result.fetchall()
    assert len(users) == 0
