import secrets
import socket
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    validator,
    Extra,
)
import psycopg2
from sqlalchemy import create_engine
from app.utils.jstruct import JStruct


class Settings(BaseSettings):
    API_V1_STR: str = "/api"

    ENVIRONMENT: str
    SERVICE: str  ## the docker service e.g. backend or celery-worker etc

    @validator("ENVIRONMENT", pre=True)
    def environment(cls, v: str) -> bool:
        if v not in {"development", "staging", "production", "testing"}:
            raise ValueError("Bad environment")
        return v

    def is_staging(self):
        return self.ENVIRONMENT == "staging"

    def is_development(self):
        return self.ENVIRONMENT == "development"

    def is_production(self):
        return self.ENVIRONMENT == "production"

    def is_testing(self):
        return self.ENVIRONMENT == "testing"

    TESTING_COLLECTION_ID: str = None
    TESTING_COLLECTION_NAME: str = None

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True
        extra = Extra.allow

        @classmethod
        def customise_sources(
                cls,
                init_settings,
                env_settings,
                file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
                # remote_config_settings_source,
            )

    def __getattr__(self, item):
        return JStruct()


settings = Settings()


def get_settings():
    return settings
