import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import Task, User
from tests.utils.constants import ADMIN_USER, MANAGER_USER, NEW_TASK, TASKS_LIST


async def add_to_db(session: AsyncSession, data: dict, model):
    instance = model(**data)
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance


@pytest.fixture
async def manager_user(async_session: AsyncSession):
    return await add_to_db(async_session, MANAGER_USER.copy(), User)


@pytest.fixture
async def admin_user(async_session: AsyncSession):
    return await add_to_db(async_session, ADMIN_USER.copy(), User)


@pytest.fixture
async def new_task(async_session: AsyncSession, admin_user: User):
    data = NEW_TASK.copy()
    data["author_id"] = admin_user.id
    return await add_to_db(async_session, data, Task)


@pytest.fixture
async def task_list(async_session: AsyncSession, admin_user: User):
    all_tasks = []
    for item in TASKS_LIST:
        data = item.copy()
        data["author_id"] = admin_user.id
        all_tasks.append(Task(**data))

    async_session.add_all(all_tasks)
    await async_session.commit()
    return all_tasks
