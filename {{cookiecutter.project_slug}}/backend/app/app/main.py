import uvicorn
from fastapi import FastAPI

from app.api.routes import api_router
from app.config import settings
from app.middlewares.base import add_profiling_middlewares
from app.middlewares.exceptions import (
    add_exceptions_middlewares
)

app = FastAPI(
    title="{{cookiecutter.project_name}}",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    openapi_tags=[],
)

add_profiling_middlewares(app)
add_exceptions_middlewares(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    if settings.is_development():
        uvicorn.run(app, host="0.0.0.0", port=80)
