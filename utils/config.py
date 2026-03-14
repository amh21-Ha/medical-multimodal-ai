from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "multimodal-medical-ai"
    app_env: str = "dev"
    log_level: str = "INFO"

    api_prefix: str = "/api/v1"
    api_key: str = Field(default="change-me", description="Simple bootstrap API key")
    allow_api_key_fallback: bool = True
    auth_mode: str = "hybrid"
    jwt_secret_key: str = "replace-this-secret"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "multimodal-medical-ai"
    jwt_audience: str = "multimodal-medical-ai-users"

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    postgres_dsn: str = "postgresql+psycopg://postgres:postgres@postgres:5432/multimodal"
    job_repository_backend: str = "memory"
    mlflow_tracking_uri: str = "http://mlflow:5000"

    storage_root: str = "./storage"
    max_upload_mb: int = 512


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
