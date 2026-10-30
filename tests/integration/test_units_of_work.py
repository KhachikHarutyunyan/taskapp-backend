from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.api.auth.repository import UserRepository
from src.api.task.repository import TaskRepository
from src.api.units_of_work import AuthUnitOfWork, TaskUnitOfWork


async def test_auth_uow_initialization(async_session: AsyncSession):
    uow = AuthUnitOfWork(async_session)

    assert isinstance(uow, AuthUnitOfWork)
    assert uow.session == async_session
    assert isinstance(uow.user_repository, UserRepository)
    assert uow.user_repository.session == async_session


async def test_task_uow_initialization(async_session: AsyncSession):
    uow = TaskUnitOfWork(async_session)

    assert isinstance(uow, TaskUnitOfWork)
    assert isinstance(uow.user_repository, UserRepository)
    assert isinstance(uow.task_repository, TaskRepository)
    assert uow.task_repository.session == async_session


async def test_auth_uow_commit_rollback(async_engine, async_session: AsyncSession):
    uow = AuthUnitOfWork(async_session)

    try:
        async with uow.atomic() as uow_ctx:
            user = await uow_ctx.user_repository.create(
                name="test",
                email="test@example.com",
                password="hashed_password",
            )
            assert user.id is not None
            raise ValueError("Test Error")
    except ValueError:
        pass

    session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
    async with session_factory() as session:
        result = await session.execute(text("SELECT * FROM users"))
        users = result.fetchall()

    assert len(users) == 0
