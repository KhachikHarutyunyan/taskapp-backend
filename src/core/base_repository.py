from typing import Generic, Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.session = session
        self.model = model

    async def get(self, id: int) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).filter(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, instance: ModelType, **kwargs) -> ModelType:
        for key, val in kwargs.items():
            setattr(instance, key, val)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        instance.deleted = True
        await self.session.flush()
        await self.session.refresh(instance)
