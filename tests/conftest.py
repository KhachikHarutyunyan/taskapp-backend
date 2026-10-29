import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine,  async_sessionmaker
from sqlalchemy.future import select

from src.api.utils.constants import Roles
from src.core.models import Role, User
from src.core.database import Base, get_session
from src.main import create_app
from src.config.settings import settings


pytest_plugins = [
    "tests.utils.create_tbs",
    "tests.utils.mocks"
]

@pytest.fixture
def test_app():
    return create_app()

@pytest.fixture(autouse=True)
def auto_clean_dependencies(test_app):
    yield
    test_app.dependency_overrides.clear()

@pytest.fixture(name="async_engine")
async def async_engine_fixture():
    # Configure and yield an async engine for your test database
    engine = create_async_engine(settings.TEST_DB_URI)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Create tables

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        for role_name in Roles:
            result = await session.execute(select(Role).where(Role.name == role_name.value))
            if not result.scalar_one_or_none():
                new_role = Role(name=role_name.value)
                session.add(new_role)
        await session.commit()

    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Clean up tables

@pytest.fixture(name="async_session")
async def async_session_fixture(async_engine):
    async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

# Clients

@pytest.fixture(name="client")
async def client_fixture(async_session, test_app):
    test_app.dependency_overrides[get_session] = lambda: async_session # Override dependency
    transport = ASGITransport(app=test_app)

    async with AsyncClient(transport=transport, base_url=f"http://test{str(settings.API_VERSION)}") as client:
        yield client

    test_app.dependency_overrides.clear() # Clear overrides after test


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user: User, async_session):
    from src.config.security import create_tokens
    access_token, refresh_token = create_tokens(admin_user.id)
    
    return access_token, refresh_token

@pytest.fixture
async def manager_token(client: AsyncClient, manager_user: User, async_session):
    from src.config.security import create_tokens
    access_token, refresh_token = create_tokens(manager_user.id)
    
    return access_token, refresh_token

@pytest.fixture()
async def admin_client(client: AsyncClient, admin_token: tuple):
    client.headers["Authorization"] = f"Bearer {admin_token[0]}"
    client.cookies["refresh_token"] = admin_token[1]
    return client

@pytest.fixture()
async def manager_client(client: AsyncClient, manager_token: tuple):
    client.headers["Authorization"] = f"Bearer {manager_token[0]}"
    client.cookies.set("refresh_token", manager_token[1])
    return client

