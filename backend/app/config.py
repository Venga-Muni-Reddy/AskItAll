import os
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AskItAll"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "temporary-secret-key-change-in-production-askitall-platform"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    # Authentication & JWT
    JWT_SECRET_KEY: str = "change-this-super-secret-jwt-key-for-askitall-platform"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day for dev convenience
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # PostgreSQL Database
    POSTGRES_USER: str = "askitall"
    POSTGRES_PASSWORD: str = "askitall_password"
    POSTGRES_DB: str = "askitall_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None
    DATABASE_URL_SYNC: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_async_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str) and v:
            return v
        data = info.data
        user = data.get("POSTGRES_USER", "askitall")
        pwd = data.get("POSTGRES_PASSWORD", "askitall_password")
        host = data.get("POSTGRES_HOST", "postgres")
        port = data.get("POSTGRES_PORT", 5432)
        db = data.get("POSTGRES_DB", "askitall_db")
        return f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}"

    @field_validator("DATABASE_URL_SYNC", mode="before")
    @classmethod
    def assemble_sync_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str) and v:
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+psycopg2://", 1)
            return v
        data = info.data
        user = data.get("POSTGRES_USER", "askitall")
        pwd = data.get("POSTGRES_PASSWORD", "askitall_password")
        host = data.get("POSTGRES_HOST", "postgres")
        port = data.get("POSTGRES_PORT", 5432)
        db = data.get("POSTGRES_DB", "askitall_db")
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"

    # Redis & Celery
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # Neo4j Graph Database
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "askitall_graph_password"
    NEO4J_DATABASE: str = "neo4j"

    # Storage
    STORAGE_BACKEND: str = "local"  # local | cloudinary | s3
    LOCAL_STORAGE_DIR: str = "/app/uploads"
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET_NAME: Optional[str] = None

    # AI Gateway Providers
    DEFAULT_LLM_PROVIDER: str = "gemini"
    DEFAULT_LLM_MODEL: str = "gemini-1.5-pro"
    DEFAULT_EMBEDDING_PROVIDER: str = "gemini"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-004"

    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"

    # Reranker
    RERANKER_PROVIDER: str = "local"
    COHERE_API_KEY: Optional[str] = None

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
