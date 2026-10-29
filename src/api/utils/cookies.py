from fastapi import Response

from src.config.settings import settings


def set_refresh_token_cookie(response: Response, token: str):
    response.delete_cookie(
        key="refresh_token",
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        # security=True, # uncomment with HTTPS
        samesite="Lax",
        max_age=settings.JWT_REFRESH_EXPIRE
        * 60,  # max age for refresh cookie in seconds
        expires=settings.JWT_REFRESH_EXPIRE
        * 60,  # expiration for refresh cookie in seconds
        path="/",
    )
