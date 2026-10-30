import fnmatch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api.dependencies import get_redis, get_session
from src.config.security import create_tokens
from src.config.settings import settings
from src.core.database import Base
from src.core.models import User
from src.main import create_app

pytest_plugins = [
    "tests.utils.create_tbs",
    "tests.utils.mocks",
]


class FakeRedis:
    """In-memory Redis stand-in so task cache calls do not need a server."""

    def __init__(self):
        self.store: dict[str, str] = {}

    async def get(self, key: str):
        return self.store.get(key)

    async def setex(self, key: str, ttl: int, value: str):
        self.store[key] = value

    async def keys(self, pattern: str):
        return [key for key in self.store if fnmatch.fnmatch(key, pattern)]

    async def delete(self, *keys: str):
        for key in keys:
            self.store.pop(key, None)


@pytest.fixture
def test_app():
    return create_app()


@pytest.fixture(autouse=True)
def auto_clean_dependencies(test_app):
    yield
    test_app.dependency_overrides.clear()


@pytest.fixture(name="async_engine")
async def async_engine_fixture():
    engine = create_async_engine(settings.TEST_DB_URI)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(name="async_session")
async def async_session_fixture(async_engine):
    session_factory = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest.fixture(name="client")
async def client_fixture(async_engine, test_app):
    session_factory = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_session():
        async with session_factory() as session:
            yield session

    test_app.dependency_overrides[get_session] = override_get_session
    test_app.dependency_overrides[get_redis] = lambda: FakeRedis()
    transport = ASGITransport(app=test_app)

    async with AsyncClient(
        transport=transport, base_url=f"http://test{settings.API_VERSION}"
    ) as client:
        yield client

    test_app.dependency_overrides.clear()


@pytest.fixture
async def admin_token(admin_user: User):
    return create_tokens(admin_user.id)


@pytest.fixture
async def manager_token(manager_user: User):
    return create_tokens(manager_user.id)


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
