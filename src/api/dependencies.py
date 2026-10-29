
from fastapi import Depends, Request
from jose import JWTError, jwt, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

from src.api.auth.service import AuthService
from src.api.exceptions import PermissionDeniedException, UnauthorizedException
from src.api.task.service import TaskService
from src.api.units_of_work import (
    AuthUnitOfWork,
    TaskUnitOfWork,
)
from src.config.security import get_token_payload, oauth2_schema
from src.config.settings import settings
from src.core.database import get_session
from src.config.logs import logger


# Redis dependencies
async def get_redis(request: Request) -> Redis:
    """Return connection with Redis"""
    return request.app.state.redis


# Auth dependencies
async def get_auth_uow(session: AsyncSession = Depends(get_session)):
    return AuthUnitOfWork(session)


async def get_auth_service(uow: AuthUnitOfWork = Depends(get_auth_uow)):
    return AuthService(uow)


# Task dependencies
async def get_task_uow(session: AsyncSession = Depends(get_session)):
    return TaskUnitOfWork(session)


async def get_task_service(uow: TaskUnitOfWork = Depends(get_task_uow)):
    return TaskService(uow)


# Security dependencies
async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_schema),
    uow: AuthUnitOfWork = Depends(get_auth_uow),
):
    if not token:
        raise UnauthorizedException(detail="Not authenticated")

    data = get_token_payload(token, settings.JWT_ACCESS_SECRET_KEY)

    if data.get("is_expire"):
        raise UnauthorizedException(detail="Not authorized")

    payload = data.get("payload")
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException(detail="Not authorized")

    if not data.get("is_expire") and payload:
        user_id = payload.get("sub")
        user = await uow.user_repository.get(user_id)
        if user:
            return user

    raise UnauthorizedException(detail="Not authorized")


class CheckRole:

    def __init__(self, roles: list[str]):
        self.roles = roles

    async def __call__(self, user=Depends(get_current_user)) -> None:
        if user.role.name not in self.roles:
            raise PermissionDeniedException()
        return user


async def get_user_id_from_refresh_token(
    request: Request,
    token: str = Depends(oauth2_schema),
) -> str:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException(detail="Refresh token is missing")

    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_REFRESH_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except ExpiredSignatureError:
        headers = {
            "Set-Cookie": (
                "refresh_token=invalid; Path=/; "
                "expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; SameSite=Lax"
            )
        }
        raise UnauthorizedException(detail="Refresh token expired", headers=headers)
    except JWTError:
        headers = {
            "Set-Cookie": (
                "refresh_token=invalid; Path=/; "
                "expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; SameSite=Lax"
            )
        }
        raise UnauthorizedException(detail="Invalid refresh token", headers=headers)

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(detail="Invalid refresh token payload")

    if token:
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            token_sub = unverified.get("sub")
            if token_sub and token_sub != user_id:
                logger.warning(f"Access token sub mismatch: {token_sub} vs {user_id}")
                raise UnauthorizedException(detail="Token mismatch")
        except JWTError:
            logger.debug("Access token is malformed or not a JWT, ignoring.")
        except Exception as e:
            logger.error(f"Unexpected error during access token inspection: {e}")

    return user_id
