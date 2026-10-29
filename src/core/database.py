from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.config.settings import settings

Base = declarative_base()

engine = create_async_engine(settings.DATABASE_URI, pool_pre_ping=True, pool_size=20)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    async with async_session_factory() as session:
        yield session
