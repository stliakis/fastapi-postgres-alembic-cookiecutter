from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings


def add_exceptions_middlewares(app):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
            request: Request, exc: RequestValidationError
    ):
        errors = {}

        for error in exc.errors():
            if error.get("loc"):
                errors[error.get("loc")[-1]] = {
                    "message": error.get("msg"),
                    "error_type": error.get("type"),
                }

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"errors": errors}),
        )

    @app.exception_handler(Exception)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=jsonable_encoder({"error": "Something went wrong"}),
        )
