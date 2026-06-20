"""
infrastructure/persistence/database.py — Database connection & session setup

Configures the SQLAlchemy 2.0 async engine and session factory.
Provides the declarative base for all ORM models.
"""

from __future__ import annotations

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# ── Async Engine Setup ───────────────────────────────────────────────────────
# We use asyncpg driver for PostgreSQL. Connection pooling is configured here.
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Automatically tests connection health
)

# ── Session Factory ──────────────────────────────────────────────────────────
# expire_on_commit=False prevents attributes from being expired after commit,
# which is crucial for async workflows where lazy loading is not possible.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ── Declarative Base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    Provides standard __repr__ and metadata binding.
    """
    pass


# ── Dependency Injection Helper ──────────────────────────────────────────────
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session and closes it after.
    Usage:
        @router.get(...)
        async def endpoint(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            # session is closed automatically by the async with context block
