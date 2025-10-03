# Purpose: Главный FastAPI приложение с роутингом и middleware.
# Context: Entry point for REST API with CORS, error handling, and health checks.
# Requirements: Load config, setup logging, register routes, handle CORS.

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from app.core import setup_logging, get_logger, settings, FamilyHabitError
from app.db import init_db, close_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for FastAPI app."""
    # Startup
    setup_logging()
    logger.info(f"Starting Family Habit API in {settings.environment} mode")
    
    if not settings.is_production:
        await init_db()
    
    yield
    
    # Shutdown
    await close_db()
    logger.info("Family Habit API stopped")


app = FastAPI(
    title="Family Habit API",
    description="API для семейного трекера привычек",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшне указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(FamilyHabitError)
async def family_habit_error_handler(request: Request, exc: FamilyHabitError):
    """Обработчик кастомных исключений."""
    logger.warning(f"Domain error: {exc.code} - {exc.message}")
    
    status_codes = {
        "validation_error": 400,
        "not_found": 404,
        "permission_denied": 403,
        "limit_exceeded": 402,
    }
    
    # Определяем HTTP код по типу ошибки
    status_code = 400
    if "not_found" in exc.code:
        status_code = 404
    elif "permission" in exc.code or "access" in exc.code:
        status_code = 403
    elif "limit" in exc.code:
        status_code = 402
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.get("/healthz")
async def health_check():
    """Проверка здоровья API."""
    return {"status": "ok", "environment": settings.environment}


@app.get("/version")
async def version_info():
    """Информация о версии."""
    git_sha = os.getenv("GIT_SHA", "unknown")
    return {
        "version": "1.0.0",
        "git_sha": git_sha,
        "environment": settings.environment
    }


# API Routes
from app.api.routes import auth, tasks, children, checkins, points

app.include_router(auth.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(children.router, prefix="/api/v1")
app.include_router(checkins.router, prefix="/api/v1")
app.include_router(points.router, prefix="/api/v1")