"""
app/main.py — FastAPI Application Entry Point
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
import sys

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api.v1.router import api_router
from app.infrastructure.persistence.database import Base, engine
import app.infrastructure.persistence.models  # Ensure all models are registered
from app.domain.exceptions.domain_exception import (
    DomainException,
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException,
)

# ── Logging Configuration ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("app.main")

settings = get_settings()

# ── Lifespan Context Manager ─────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup event ──────────────────────────────────────────────────────────
    logger.info("Starting up FastAPI application...")
    
    # 1. Verify critical configurations
    logger.info("Verifying configuration settings...")
    is_default = (not settings.jwt_secret_key) or (settings.jwt_secret_key == "dev_secret_key_change_me_in_production")
    is_short = settings.jwt_secret_key and len(settings.jwt_secret_key) < 32
    
    if settings.environment == "production":
        if is_default:
            logger.critical("Insecure JWT_SECRET_KEY default rejected in production!")
            raise RuntimeError("JWT_SECRET_KEY cannot be default in production mode.")
        if is_short:
            logger.critical("JWT_SECRET_KEY length must be at least 32 characters in production!")
            raise RuntimeError("JWT_SECRET_KEY length must be at least 32 characters in production.")
    else:
        if is_default:
            logger.warning(
                "JWT_SECRET_KEY is using the default development key. "
                "Please ensure a secure key is set in production environment!"
            )
        elif is_short:
            logger.warning(
                "JWT_SECRET_KEY length is less than 32 characters. "
                "Ensure a longer secure key is configured for production!"
            )
    
    # 2. Database Initialization / Connectivity Check
    logger.info("Initializing database and verifying connection...")
    try:
        async with engine.begin() as conn:
            # Sync tables structure (safe check, does CREATE TABLE IF NOT EXISTS)
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}")
        # We don't crash startup immediately in case DB is temporarily down,
        # but log as critical.
    
    logger.info("FastAPI Application initialization complete.")
    yield
    
    # ── Shutdown event ─────────────────────────────────────────────────────────
    logger.info("Shutting down application...")
    logger.info("Disposing database connection engine...")
    await engine.dispose()
    logger.info("Application shutdown complete.")


# ── FastAPI App Instance ─────────────────────────────────────────────────────
app = FastAPI(
    title="AI Answer Evaluation System API",
    description=(
        "Backend REST API for the AI Answer Evaluation System. "
        "Provides authentication, exam & student management, OCR processing, "
        "and automated rubric-based grading."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Trusted Host Middleware ──────────────────────────────────────────────────
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts,
)


# ── Global Exception Handlers ─────────────────────────────────────────────────
@app.exception_handler(EntityNotFoundException)
async def entity_not_found_exception_handler(request: Request, exc: EntityNotFoundException):
    logger.warning(f"EntityNotFoundException: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


@app.exception_handler(DuplicateEntityException)
async def duplicate_entity_exception_handler(request: Request, exc: DuplicateEntityException):
    logger.warning(f"DuplicateEntityException: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


@app.exception_handler(BusinessRuleViolationException)
async def business_rule_violation_exception_handler(request: Request, exc: BusinessRuleViolationException):
    logger.warning(f"BusinessRuleViolationException: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    logger.warning(f"DomainException: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


# ── Health Endpoint ──────────────────────────────────────────────────────────
@app.get("/health", status_code=status.HTTP_200_OK, tags=["System Health"])
async def health_check():
    """
    Health check endpoint to verify backend service readiness.
    """
    return {"status": "healthy"}


# ── Register Routers ─────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")
