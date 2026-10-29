from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


class BaseUnitOfWork:

    def __init__(self, session: AsyncSession):
        self.session = session

    @asynccontextmanager
    async def atomic(self):
        try:
            yield self
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()
