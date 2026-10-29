from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from redis.asyncio import Redis
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.api.endpoints import routes
from src.api.error_handlers import register_error_handlers
from src.api.utils import ORIGINS
from src.config.settings import settings
from src.external_services.redis.rate_limit import get_limiter
from src.external_services import redis_pool


def create_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.redis = Redis(connection_pool=redis_pool)
        yield
        await app.state.redis.close()
        await redis_pool.aclose()

    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    limiter = get_limiter()
    app.state.limiter = limiter

    # Middlewares
    app.add_middleware(
        SessionMiddleware, secret_key=settings.SECRET_KEY, session_cookie="session"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[*ORIGINS],  # Origins list
        allow_credentials=True,
        allow_headers=["*"],
        allow_methods=["*"],
        expose_headers=["Set-Cookie", "set-cookie"],
    )

    app.add_middleware(SlowAPIMiddleware)

    # Register application error handlers
    register_error_handlers(app)

    # Documentation
    @app.get(f"{settings.API_VERSION}/docs/openapi.json", include_in_schema=False)
    async def openapi():
        return get_openapi(title=app.title, version=app.version, routes=app.routes)

    @app.get("/api/v1/docs", include_in_schema=False)
    async def get_swagger_documentation():
        return get_swagger_ui_html(
            openapi_url=f"{settings.API_VERSION}/docs/openapi.json",
            title=settings.APP_NAME,
            swagger_ui_parameters={
                "defaultModelsExpandDepth": -1,
                "docExpansion": "none",
                "displayRequestDuration": True,
                "requestInterceptor": """
                    request => {
                        request.headers['X-From-Swagger'] = 'true'
                        return request
                    }
                """,
            },
        )

    # Routes
    app.include_router(routes, prefix=settings.API_VERSION)

    return app
