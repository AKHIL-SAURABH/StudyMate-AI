"""
StudyMate AI — FastAPI Application Entry Point.

Initializes the FastAPI app, registers middleware, routers,
and handles startup/shutdown events.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI

# Add project root to Python path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.config import get_settings
from backend.database import db
from backend.middleware import setup_middleware
from backend.routers import auth, chat, subjects, progress, quiz, analytics
from utils.logger import setup_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    settings = get_settings()
    setup_logging(settings.log_level)
    logger = get_logger("main")

    # Startup
    logger.info("[STARTING] Starting StudyMate AI Backend...")
    await db.initialize()
    logger.info("[SUCCESS] Database initialized")
    logger.info("[INFO] API running at http://%s:%d", settings.api_host, settings.api_port)

    yield

    # Shutdown
    logger.info("[SHUTDOWN] Shutting down StudyMate AI Backend...")


# Create FastAPI application
app = FastAPI(
    title="StudyMate AI",
    description="AI-powered Study Mentor with Agentic AI, MCP, and ReAct reasoning",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Apply middleware
setup_middleware(app)

# Register routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(subjects.router)
app.include_router(progress.router)
app.include_router(quiz.router)
app.include_router(analytics.router)


@app.get("/", tags=["Health"])
async def root() -> dict:
    """Health check endpoint."""
    return {
        "service": "StudyMate AI",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Detailed health check."""
    settings = get_settings()
    return {
        "status": "healthy",
        "service": "StudyMate AI",
        "llm_model": settings.llm_primary_model,
        "database": "connected",
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )
