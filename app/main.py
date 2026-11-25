"""
GlobeTrotter AI - FastAPI Main Application Entrypoint.
Automated Global Tourism Research, Blog Generation & Publishing Platform.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import get_settings
from app.utils.logging import logger
from app.database.session import ensure_database_exists
from app.database.init_db import init_db
from app.api.routes import health, topics, research, articles, seo, images, evaluation, workflow, publishing, automation, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager for startup and shutdown procedures.
    Automatically verifies database availability and creates schema tables.
    """
    settings = get_settings()
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode...")
    logger.info(f"Configured NVIDIA Model: {settings.NVIDIA_MODEL_NAME}")
    logger.info(f"Configured NIM Endpoint : {settings.NVIDIA_BASE_URL}")

    # Ensure database exists and schema is initialized
    ensure_database_exists()
    init_db()

    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


def create_app() -> FastAPI:
    """Factory to create and configure the FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title="GlobeTrotter AI Backend",
        description=(
            "Automated Global Tourism Research, Blog Generation & Publishing Platform. "
            "Powered by LangChain, LangGraph, and NVIDIA NIM."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Enable Cross-Origin Resource Sharing (CORS) for React frontend integration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict to specific origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Enable High-Speed GZip Compression for payloads >= 500 bytes (75-80% bandwidth reduction for 1M scale)
    application.add_middleware(GZipMiddleware, minimum_size=500)

    # Register API Routers
    application.include_router(health.router, prefix="/api/v1")
    application.include_router(topics.router, prefix="/api/v1")
    application.include_router(research.router, prefix="/api/v1")
    application.include_router(articles.router, prefix="/api/v1")
    application.include_router(seo.router, prefix="/api/v1")
    application.include_router(images.router, prefix="/api/v1")
    application.include_router(evaluation.router, prefix="/api/v1")
    application.include_router(workflow.router, prefix="/api/v1")
    application.include_router(publishing.router, prefix="/api/v1")
    application.include_router(automation.router, prefix="/api/v1")
    application.include_router(auth.router, prefix="/api/v1")

    @application.get("/", tags=["Root"])
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME} API",
            "documentation": "/docs",
            "health_check": "/api/v1/health",
            "llm_check": "/api/v1/health/llm",
            "db_check": "/api/v1/health/db",
            "topics_api": "/api/v1/topics",
            "research_api": "/api/v1/research",
            "articles_api": "/api/v1/articles",
            "seo_api": "/api/v1/seo",
            "images_api": "/api/v1/images",
            "evaluation_api": "/api/v1/evaluate",
            "workflow_api": "/api/v1/workflow",
            "publishing_api": "/api/v1/publish",
            "automation_api": "/api/v1/automation",
            "public_feed": "/api/v1/publish/feed",
            "cache_telemetry": "/api/v1/publish/cache/stats",
            "react_app": "/app",
            "status": "operational",
        }

    # Mount compiled React SPA if built
    dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.exists(dist_dir) and os.path.exists(assets_dir):
        application.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @application.get("/app", tags=["Frontend"])
        @application.get("/admin", tags=["Frontend"])
        @application.get("/app/{full_path:path}", tags=["Frontend"])
        async def serve_react_app(full_path: str = ""):
            return FileResponse(os.path.join(dist_dir, "index.html"))

    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
