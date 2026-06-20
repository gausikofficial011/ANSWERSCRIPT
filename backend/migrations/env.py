"""
migrations/env.py — Alembic Migration Environment

Configures SQLAlchemy metadata and async connection for Alembic migrations.
Supports both online (live DB) and offline (SQL script generation) modes.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── Alembic Config Object ────────────────────────────────────────────────────
config = context.config

# ── Logging Setup ────────────────────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import All ORM Models for Autogenerate ────────────────────────────────────
# IMPORTANT: All model modules MUST be imported here so that
# SQLAlchemy's MetaData is populated before Alembic inspects it.
from app.infrastructure.persistence.models import (  # noqa: F401
    user_model,
    student_model,
    subject_model,
    exam_model,
    question_model,
    model_answer_model,
    answer_sheet_model,
    ocr_result_model,
    extracted_answer_model,
    evaluation_model,
    final_result_model,
    plagiarism_report_model,
    audit_log_model,
    notification_model,
)
from app.infrastructure.persistence.database import Base

# ── Target Metadata ───────────────────────────────────────────────────────────
target_metadata = Base.metadata


def get_database_url() -> str:
    """Load DATABASE_URL from application settings (not directly from env)."""
    from app.config import get_settings
    settings = get_settings()
    return str(settings.database_url)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Generates SQL scripts without connecting to the database.
    Useful for reviewing changes or applying manually.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using async SQLAlchemy engine."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


# ── Entry Point ───────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
