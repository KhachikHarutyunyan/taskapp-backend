from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_repository import BaseRepository
from src.core.models import User


class UserRepository(BaseRepository[User]):

    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = User

    async def get_by_email(self, email: str) -> User:
        result = await self.session.execute(
            select(User).where(User.email == email, User.deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()
