from fastapi import APIRouter
from redis import Redis
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config.settings import settings


redis = Redis(
    host=settings.REDIS_HOST, 
    password=settings.REDIS_PASSWORD, 
    port=6379, 
    db=0, 
    decode_responses=True
)

def get_limiter():
    return Limiter(
        key_func=get_remote_address,
        strategy="fixed-window",
        storage_uri=settings.REDIS_URL,
        enabled=settings.TESTING,
    )


def apply_limiter(router: APIRouter, limit: str, limiter: Limiter):
    for route in router.routes:
        if hasattr(route, "endpoint"):
            route.endpoint = limiter.limit(limit)(route.endpoint)
