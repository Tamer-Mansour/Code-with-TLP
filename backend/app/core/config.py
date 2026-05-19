from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Studying App"
    app_env: str = "development"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:4200"])

    database_url: str = "sqlite:///./studying_app.db"

    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 14
    algorithm: str = "HS256"

    first_admin_email: str = "admin@studying.app"
    first_admin_username: str = "admin"
    first_admin_password: str = "ChangeMe123!"

    docker_enabled: bool = True
    runner_default_timeout_sec: int = 5
    runner_default_memory_mb: int = 256
    runner_default_cpu: float = 0.5
    runner_image_python: str = "studying-runner-python:latest"
    runner_image_node: str = "studying-runner-node:latest"
    runner_image_java: str = "studying-runner-java:latest"
    runner_image_csharp: str = "studying-runner-csharp:latest"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
