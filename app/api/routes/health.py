"""
Health Check and Diagnostics Routes.
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.config import get_settings
from app.llm import check_llm_connection
from app.database.session import check_db_connection

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])


class SystemHealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    app_name: str = Field(..., example="GlobeTrotter AI")
    environment: str = Field(..., example="development")
    version: str = Field(..., example="0.1.0")
    timestamp_utc: str


@router.get("", response_model=SystemHealthResponse)
async def get_system_health():
    """Basic health check verifying the FastAPI service is running and responsive."""
    settings = get_settings()
    return SystemHealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="0.1.0",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/llm")
async def get_llm_health():
    """Performs an active check of the configured NVIDIA NIM LLM provider."""
    return await check_llm_connection()


@router.get("/db")
async def get_db_health():
    """Performs an active connectivity and dialect check of the PostgreSQL database."""
    return check_db_connection()
