from fastapi import APIRouter

from src.api.auth.routes import auth_router
from src.api.task.routes import tasks_router
from src.external_services import apply_limiter, get_limiter
from src.api.utils.constants import LIMITS

routes = APIRouter()
limiter = get_limiter()

apply_limiter(auth_router, LIMITS["auth"], limiter)
routes.include_router(auth_router, prefix="/auth", tags=["Auth"])

apply_limiter(tasks_router, LIMITS["api"], limiter)
routes.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])


# Health checking endpoint
@routes.get("/ping", tags=["health"], include_in_schema=False)
async def pong():
    return {"msg": "Pong"}
