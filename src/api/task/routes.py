from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from redis import Redis

from src.api.dependencies import get_current_user, get_redis, get_task_service
from src.api.task.schemas import (
    CreateTaskSchema,
    TaskFullResponseSchema,
    TaskResponseSchema,
    UpdateTaskSchema,
)
from src.api.task.service import TaskService
from src.core.models.user import User

tasks_router = APIRouter()


@tasks_router.post("", status_code=201)
async def create_task(
    request: Request,
    payload: CreateTaskSchema,
    service: TaskService = Depends(get_task_service),
    user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
) -> TaskResponseSchema:
    return await service.create(payload, user.id, redis)


@tasks_router.get("")
async def retrieve_tasks(
    request: Request,
    by_owner: Optional[bool] = False,
    service: TaskService = Depends(get_task_service),
    user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    return await service.retrieve_all(redis=redis, user_id=user.id, by_owner=by_owner)


@tasks_router.get("/{id}")
async def get_task(
    request: Request,
    id: UUID,
    service: TaskService = Depends(get_task_service),
    user: User = Depends(get_current_user),
) -> TaskFullResponseSchema:
    return await service.get(id)


@tasks_router.patch("/{id}")
async def update_task(
    request: Request,
    id: UUID,
    payload: UpdateTaskSchema,
    service: TaskService = Depends(get_task_service),
    user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
) -> TaskResponseSchema:
    return await service.update(id, payload, redis)


@tasks_router.delete("/{id}", status_code=204)
async def delete_task(
    request: Request,
    id: UUID,
    service: TaskService = Depends(get_task_service),
    user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    await service.delete(id, user_id=user.id, redis=redis)
