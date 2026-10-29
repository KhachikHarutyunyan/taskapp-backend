import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.utils.constants import Roles
from src.core.models import Role, User, Task
from tests.utils.constants import MANAGER_USER, NEW_TASK, NEW_USER, TASKS_LIST, WORKER_USER, ADMIN_USER, UNVERIFIED_USER, INACTIVE_USER


async def add_to_db(session: AsyncSession, data: dict, model):
    instance = model(**data)
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance

@pytest.fixture
async def unverified_user(async_session: AsyncSession):
    ext = await async_session.execute(select(Role).where(Role.name==Roles.MANAGER.value))
    role = ext.scalar_one()
    UNVERIFIED_USER["role_id"] = role.id
    return await add_to_db(async_session, UNVERIFIED_USER, User)

@pytest.fixture
async def inactive_user(async_session: AsyncSession):
    ext = await async_session.execute(select(Role).where(Role.name==Roles.MANAGER.value))
    role = ext.scalar_one()
    INACTIVE_USER["role_id"] = role.id
    return await add_to_db(async_session, INACTIVE_USER, User)

@pytest.fixture
async def new_user(async_session: AsyncSession):
    ext = await async_session.execute(select(Role).where(Role.name==Roles.WORKER.value))
    role = ext.scalar_one()
    NEW_USER["role_id"] = role.id
    return await add_to_db(async_session, NEW_USER, User)

@pytest.fixture
async def worker_user(async_session: AsyncSession):
    ext = await async_session.execute(select(Role).where(Role.name==Roles.WORKER.value))
    role = ext.scalar_one()
    WORKER_USER["role_id"] = role.id
    return await add_to_db(async_session, WORKER_USER, User)

@pytest.fixture
async def manager_user(async_session: AsyncSession):
    ext = await async_session.execute(select(Role).where(Role.name==Roles.MANAGER.value))
    role = ext.scalar_one()
    MANAGER_USER["role_id"] = role.id
    return await add_to_db(async_session, MANAGER_USER, User)

@pytest.fixture
async def admin_user(async_session: AsyncSession):
    ext = await async_session.execute(select(Role).where(Role.name==Roles.ADMIN.value))
    role = ext.scalar_one()
    ADMIN_USER["role_id"] = role.id
    return await add_to_db(async_session, ADMIN_USER, User)

@pytest.fixture
async def new_task(async_session: AsyncSession, admin_user: User, manager_user: User):
    data = NEW_TASK.copy()
    data["author_id"] = admin_user.id
    data["executors"] = [admin_user, manager_user]
    return await add_to_db(async_session, data, Task)

@pytest.fixture
async def task_list(async_session: AsyncSession, admin_user: User, manager_user: User):
    all_tasks = []
    for i in range(0, len(TASKS_LIST)):
        data = TASKS_LIST[i]
        data["author_id"] = admin_user.id
        if i % 2:
            data["executors"] = [manager_user]
        elif i % 5:
            data["executors"] = [admin_user, manager_user]
        else:
            data["executors"] = []
        all_tasks.append(Task(**data))
    
    async_session.add_all(all_tasks)
    await async_session.commit()
    return all_tasks

