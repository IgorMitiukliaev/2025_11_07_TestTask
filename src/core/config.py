import os
from typing import List
from pydantic import field_validator, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        case_sensitive=False,
        extra="ignore",
    )
    APP_NAME: str = Field("Incident Management API", description="Application name")
    APP_VERSION: str = Field("0.1.0", description="Application version")

    POSTGRES_HOST: str = Field("app_db", description="Database host")
    POSTGRES_PORT: Optional[int] = Field(5432, description="Database port")
    POSTGRES_DB: str = Field("incidents_db", description="Database name")
    POSTGRES_SCHEMA: str = Field("public", description="Database schema")
    POSTGRES_USER: str = Field("postgres", description="Database user")
    POSTGRES_PASSWORD: Optional[str] = Field(
        None, description="Database password for postgres user"
    )
    BACKEND_USER: str = Field(
        "backend", description="Database user for backend app"
    )
    BACKEND_PASSWORD: str = Field(
        "backend", description="Database password for backend user"
    )

    # Web server configuration
    HOST: str = Field("0.0.0.0", description="Web server host")
    PORT: int = Field(8000, description="Web server port")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        username = self.BACKEND_USER
        password = self.BACKEND_PASSWORD

        return str(
            f"postgresql+asyncpg://{username}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def get_uvicorn_config(self) -> dict:
        return {
            "host": self.HOST,
            "port": self.PORT,
            "reload": True,
            "access_log": True,
            "reload_excludes": ["*.log", "*.db", ".env*"],
        }

    def get_app_metadata(self) -> dict:
        return {
            "title": self.APP_NAME,
            "version": self.APP_VERSION,
            "openapi_version": "3.0.2",
            "openapi_url": "/swagger/openapi.json",
            "docs_url": "/swagger/",
            "redoc_url": "/redoc",
        }

    def get_db_config(self) -> dict:
        return {
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
            "database": self.POSTGRES_DB,
            "user": self.BACKEND_USER,
            "password": self.BACKEND_PASSWORD,
            "schema": self.POSTGRES_SCHEMA,
            "url": self.DATABASE_URL,
        }


app_config = Settings()
