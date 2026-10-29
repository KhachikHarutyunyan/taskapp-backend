from uuid import UUID

from redis import Redis
from src.api.exceptions import NotFoundException, PermissionDeniedException
from src.api.task.dto_factory import TasksDTOFactory
from src.api.task.schemas import (
    CreateTaskSchema,
    TaskFullResponseSchema,
    TaskResponseSchema,
    UpdateTaskSchema,
)
from src.external_services.redis.cache import CacheService
from src.api.units_of_work import TaskUnitOfWork
from src.core.models import Task


class TaskService:

    def __init__(self, uow: TaskUnitOfWork):
        self.uow = uow
        self.cache_prefix = "cameras"

    async def create(
        self, payload: CreateTaskSchema,
        author_id: int,
        redis: Redis
    ) -> TaskResponseSchema:
        async with self.uow.atomic() as uow:
            task = await uow.task_repository.create(
                name=payload.name,
                description=payload.description,
                author_id=author_id,
            )
            await self.__invalidate_cache(redis)
            return TasksDTOFactory.create_base_dto(task)

    async def retrieve_all(self, redis: Redis, user_id: UUID, by_owner: bool = False):
        async with self.uow.atomic() as uow:
            cache_service = CacheService(redis, self.cache_prefix)
            cache_params = {
                "user_id": str(user_id),
                "prefix": "retrieve_all",
                "by_owner": by_owner
            }
            if cached := await cache_service.get_list_cache(cache_params):
                return cached
            
            if by_owner:
                tasks = await uow.task_repository.get_user_tasks(user_id)
            else:
                tasks = await uow.task_repository.get_all()

            result = [TasksDTOFactory.create_dto_for_list(task) for task in tasks]
            await cache_service.set_list_cache(cache_params, result, 180)
            return result

    async def get(self, id: UUID) -> TaskFullResponseSchema:
        async with self.uow.atomic() as uow:
            task = await self._check_task(id, uow)
            return TasksDTOFactory.create_full_dto(task)

    async def update(self, id: UUID, payload: UpdateTaskSchema, redis: Redis) -> TaskResponseSchema:
        async with self.uow.atomic() as uow:
            task = await self._check_task(id, uow)
            data = payload.model_dump(exclude_none=True)
            if not data:
                return TasksDTOFactory.create_full_dto(task)

            result = await uow.task_repository.update(task, **data)
            await self.__invalidate_cache(redis)
            return TasksDTOFactory.create_full_dto(result)

    async def delete(self, id: UUID, user_id: UUID, redis: Redis) -> None:
        async with self.uow.atomic() as uow:
            task = await self._check_task(id, uow)
            if task.author_id != user_id:
                raise PermissionDeniedException()
            await uow.task_repository.delete(task)
            await self.__invalidate_cache(redis)

    async def _check_task(self, id: UUID, uow: TaskUnitOfWork) -> Task:
        task = await uow.task_repository.get(id)
        if task is None:
            raise NotFoundException()
        return task

    async def __invalidate_cache(self, redis: Redis):
        cache_service = CacheService(redis, self.cache_prefix)
        await cache_service.invalidate_list_cache()