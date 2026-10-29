from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_repository import BaseRepository
from src.core.models import Task


class TaskRepository(BaseRepository[Task]):

    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Task

    async def get(self, id: UUID) -> Task:
        result = await self.session.execute(
            select(Task).where(Task.id == id, Task.deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Task]:
        result = await self.session.execute(select(Task).where(Task.deleted.is_(False)))
        return result.scalars().all()

    async def get_user_tasks(self, user_id: UUID) -> List[Task]:
        result = await self.session.execute(select(Task).where(Task.author_id==user_id, Task.deleted.is_(False)))
        return result.scalars().all()
