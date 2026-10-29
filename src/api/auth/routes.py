from datetime import timedelta

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.auth.schemas import LoginSchema, RequestUserSchema, ResponseUserSchema, TokenResponse
from src.api.auth.service import AuthService
from src.api.dependencies import (
    get_auth_service,
    get_current_user,
    get_user_id_from_refresh_token,
)
from src.api.exceptions import PasswordsDoNotMatchException
from src.api.utils.cookies import set_refresh_token_cookie
from src.config.security import create_tokens, generate_token
from src.config.settings import settings
from src.core.models.user import User

auth_router = APIRouter()


# LOCAL AUTH


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    payload: RequestUserSchema,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    if payload.password != payload.confirm_password:
        raise PasswordsDoNotMatchException()

    del payload.confirm_password

    result = await service.register(payload)

    at_expires = timedelta(minutes=settings.JWT_ACCESS_EXPIRE)
    at_token = generate_token(result.id, at_expires, settings.JWT_ACCESS_SECRET_KEY)
    return {"access_token": at_token}


@auth_router.post("/login")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    data = LoginSchema(email=form_data.username, password=form_data.password)
    result = await service.login(data)
    access_token, refresh_token = create_tokens(result.id)

    # save refresh token to cookies
    set_refresh_token_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@auth_router.post("/logout")
async def logout(
    request: Request, response: Response, user: User = Depends(get_current_user)
):
    response.delete_cookie("refresh_token")
    return {"detail": "Successfully logged out"}

@auth_router.get("/me", response_model=ResponseUserSchema)
async def show_me(
    request: Request, user: User = Depends(get_current_user)
) -> ResponseUserSchema:
    return user


@auth_router.post("/refresh_token")
async def refresh_token(
    request: Request,
    user_id: str = Depends(get_user_id_from_refresh_token),
) -> TokenResponse:
    at_expires = timedelta(minutes=settings.JWT_ACCESS_EXPIRE)
    access_token = generate_token(
        user_id, at_expires, settings.JWT_ACCESS_SECRET_KEY
    )
    return TokenResponse(access_token=access_token)
