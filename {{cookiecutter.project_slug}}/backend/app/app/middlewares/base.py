from fastapi_utils.timing import add_timing_middleware
from starlette.middleware.cors import CORSMiddleware

from app.config import settings


def add_profiling_middlewares(app):
    add_timing_middleware(app, record=print, prefix="app", exclude="untimed")


def add_cors_middlewares(app):
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
