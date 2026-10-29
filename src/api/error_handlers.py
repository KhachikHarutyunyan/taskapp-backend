from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.api.exceptions import AppException
from src.config.logs import logger


def register_error_handlers(app: FastAPI):

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
        # ERROR_COUNT.labels(
        #     method=request.method,
        #     endpoint=request.url.path,
        #     exception_type=exc.__class__.__name__,
        #     http_status=400
        # )

        error_details = []
        for error in exc.errors():
            field = " -> ".join([str(loc) for loc in error.get("loc", [])])
            msg = error.get("msg", "Validation error")
            error_details.append(f"{field}: {msg}")

        error_message = (
            "; ".join(error_details) if error_details else "Validation error"
        )

        logger.error(
            f"Validation error: msg='{error_message}', path='{request.url.path}',\
            method='{request.method}', status_code='422'",
            exc_info=True,
        )
        return JSONResponse(
            status_code=422,
            content={"detail": error_message},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request, exc: RequestValidationError
    ):
        # ERROR_COUNT.labels(
        #     method=request.method,
        #     endpoint=request.url.path,
        #     exception_type=exc.__class__.__name__,
        #     http_status=400
        # )

        error_details = []
        for error in exc.errors():
            field = " -> ".join([str(loc) for loc in error.get("loc", [])])
            msg = error.get("msg", "Validation error")
            error_details.append(f"{field}: {msg}")

        error_message = (
            "; ".join(error_details) if error_details else "Validation error"
        )

        logger.error(
            f"Request validation error: msg='{error_message}', \
            path='{request.url.path}', method='{request.method}', status_code='422'",
            exc_info=True,
        )
        return JSONResponse(
            status_code=422,
            content={"detail": error_message},
        )

    @app.exception_handler(AppException)
    async def api_error_handler(request: Request, exc: AppException):
        # ERROR_COUNT.labels(
        #     method=request.method,
        #     endpoint=request.url.path,
        #     exception_type=exc.__class__.__name__,
        #     http_status=exc.status_code
        # )

        logger.error(
            f"Error: msg='{exc.detail}', path='{request.url.path}', \
            method='{request.method}', status_code='{exc.status_code}'",
            exc_info=True,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers if hasattr(exc, "headers") else None,
        )

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException):
        # ERROR_COUNT.labels(
        #     method=request.method,
        #     endpoint=request.url.path,
        #     exception_type=exc.__class__.__name__,
        #     http_status=exc.status_code
        # )

        logger.error(
            f"Error: msg='{exc.detail}', path='{request.url.path}',\
            method='{request.method}', status_code='{exc.status_code}'",
            exc_info=True,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers if hasattr(exc, "headers") else None,
        )

    @app.exception_handler(Exception)
    async def univeral_error_handler(request: Request, exc: Exception):
        # ERROR_COUNT.labels(
        #     method=request.method,
        #     endpoint=request.url.path,
        #     exception_type=exc.__class__.__name__,
        #     http_status=500
        # )

        logger.critical(
            f"Error: msg='{exc}', path='{request.url.path}', \
            method='{request.method}', status_code='500'",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )
