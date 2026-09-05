from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions import AppException


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception
    ):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error"
            }
        )