from uuid import uuid4
import pytest
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.utils.constants import Roles
from src.api.account.repository import UserRepository, RolesRepository

async def test_user_repository_crud(async_session: AsyncSession):
    repo = UserRepository(async_session)

    from src.core.models import Role
    result = await async_session.execute(select(Role).where(Role.name == Roles.WORKER.value))
    role = result.scalar_one()

    # Create
    user = await repo.create(
        name="test", 
        email="test@example.com", 
        password="hashed_password",
        role_id=role.id
    )
    assert user.id is not None

    # Read
    fetched = await repo.get(user.id)
    assert fetched.email == "test@example.com"

    fake_user = await repo.get(uuid4())
    assert fake_user is None

    # Get by email
    user_by_email = await repo.get_by_email("test@example.com")
    assert user_by_email is not None
    assert user_by_email.name == "test"

    fake_user = await repo.get_by_email("fake@mail.com")
    assert fake_user is None

    fake_user = await repo.get_by_email("TeSt@example.com")
    assert fake_user.email == "test@example.com"
    assert fake_user.name == "test"

    # Get all
    all_users = await repo.get_all()
    assert all_users is not None
    assert all_users == [user]

    # Update
    update = await repo.update(user, email="update@mail.com")
    assert update.email == "update@mail.com"

    # Delete
    delete = await repo.delete(user)
    assert delete == None

async def test_role_repository_crud(async_session: AsyncSession):
    repo = RolesRepository(async_session)
    NAME = "New Role"

    # Create
    role = await repo.create(name=NAME)
    assert role.id is not None

    # Read
    fetched = await repo.get(role.id)
    assert fetched.id == role.id
    assert fetched.name == NAME

    fetched_by_name = await repo.get_by_name(NAME)
    assert fetched_by_name.name == NAME

    # Update
    update = await repo.update(role, name="UPDATE")
    assert update.name == "UPDATE"

    # delete
    delete = await repo.delete(role)
    assert delete is None





