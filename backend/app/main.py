from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text

from app.config import settings
from app.core.exceptions import AppException, app_exception_handler, validation_exception_handler
from app.core.middleware import RequestIdMiddleware
from app.api.v1.api import api_router
from app.db.session import engine
from app.db.base import Base
import app.db.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatic schema initialization for development convenience
    async with engine.begin() as conn:
        # Create schemas
        schemas = [
            "identity", "organization", "knowledge", "ingestion",
            "retrieval", "conversation", "memory", "ai", "usage", "audit"
        ]
        for s in schemas:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {s};"))
        # Enable extensions
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="AskItAll - Enterprise Multimodal Knowledge Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Request ID & Tracing Middleware
app.add_middleware(RequestIdMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers for standard error contract
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Mount API V1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0",
    }
