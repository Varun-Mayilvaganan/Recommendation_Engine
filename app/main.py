"""FastAPI application entrypoint - MVC backend with SHL recommendation pipeline."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers import recommendation_router, user_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.logger import logger
from app.utils.response import success_response


def _init_db() -> None:
    """Create database tables. Called on startup."""
    from app.models import User  # noqa: F401
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables on startup."""
    logger.info("Starting %s", settings.app_name)
    _init_db()
    logger.info("Database tables created")
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description="SHL Assessment Recommendation API - MVC backend with GenAI pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router)
app.include_router(recommendation_router)

# Ensure DB tables exist on import (for TestClient, script runners)
_init_db()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return success_response(
        data={"status": "ok", "app": settings.app_name},
        message="Service healthy",
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return success_response(
        data={
            "app": settings.app_name,
            "docs": "/docs",
            "health": "/health",
            "endpoints": ["/users", "/recommend"],
        },
        message="Welcome",
    )
