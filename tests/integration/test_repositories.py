from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.repository import UserRepository
from src.api.task.repository import TaskRepository
from src.core.models import User


async def test_user_repository_crud(async_session: AsyncSession):
    repo = UserRepository(async_session)

    user = await repo.create(
        name="test",
        email="test@example.com",
        password="hashed_password",
    )
    assert user.id is not None

    fetched = await repo.get(user.id)
    assert fetched.email == "test@example.com"

    missing = await repo.get(uuid4())
    assert missing is None

    user_by_email = await repo.get_by_email("test@example.com")
    assert user_by_email is not None
    assert user_by_email.name == "test"

    assert await repo.get_by_email("fake@mail.com") is None
    assert await repo.get_by_email("TeSt@example.com") is None

    all_users = await repo.get_all()
    assert all_users == [user]

    updated = await repo.update(user, email="update@mail.com")
    assert updated.email == "update@mail.com"

    deleted = await repo.delete(user)
    assert deleted is None
    assert user.deleted is True


async def test_task_repository_crud(async_session: AsyncSession):
    user = User(name="author", email="author@example.com", password="hashed")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    repo = TaskRepository(async_session)
    task = await repo.create(
        name="Repo task",
        description="Repository coverage",
        author_id=user.id,
    )
    assert task.id is not None

    fetched = await repo.get(task.id)
    assert fetched.name == "Repo task"

    assert await repo.get(uuid4()) is None

    owned = await repo.get_user_tasks(user.id)
    assert owned == [task]

    all_tasks = await repo.get_all()
    assert task in all_tasks

    updated = await repo.update(task, name="Updated repo task")
    assert updated.name == "Updated repo task"

    await repo.delete(task)
    assert await repo.get(task.id) is None
