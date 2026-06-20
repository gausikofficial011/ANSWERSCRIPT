"""
tasks/cleanup_tasks.py — File Lifecycle Cleanup Celery Tasks

Periodic and event-driven cleanup tasks for the file storage subsystem.
Triggered by Celery Beat schedule (defined in celery_app.py).

Tasks:
  cleanup_temporary_files   — Runs every 2 hours (beat schedule)
  cleanup_expired_reports   — Runs daily at 2 AM UTC (beat schedule)
  cleanup_job_temp_dir      — Triggered when OCR/Eval job ends

All tasks use the FileCategory and RetentionPolicy definitions
from app.storage.lifecycle.retention_policy.
"""

from __future__ import annotations

from celery.utils.log import get_task_logger

from app.tasks.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_temporary_files",
    queue="cleanup",
    max_retries=1,
    time_limit=300,
)
def cleanup_temporary_files() -> dict:
    """
    Periodic task: Remove all temporary files older than 2 hours.
    Runs every 2 hours via Celery Beat.

    Returns:
        {"deleted_count": int, "freed_bytes": int}
    """
    logger.info("Cleanup: temporary files scan started")
    raise NotImplementedError("Cleanup task implementation pending Phase 12.")


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_expired_reports",
    queue="cleanup",
    max_retries=1,
    time_limit=600,
)
def cleanup_expired_reports() -> dict:
    """
    Periodic task: Remove PDF reports older than 1 year (365 days).
    Runs daily via Celery Beat.

    Returns:
        {"deleted_count": int, "freed_bytes": int}
    """
    logger.info("Cleanup: expired reports scan started")
    raise NotImplementedError("Cleanup task implementation pending Phase 12.")


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_job_temp_dir",
    queue="cleanup",
    max_retries=2,
    time_limit=60,
)
def cleanup_job_temp_dir(job_id: str) -> dict:
    """
    Event-driven task: Clean up the temporary directory for a completed/failed job.
    Called at the end of OCR and evaluation tasks via Celery chain or signal.

    Args:
        job_id: The UUID of the processing job whose temp dir should be removed.

    Returns:
        {"job_id": str, "deleted_files": int}
    """
    logger.info("Cleanup: job temp dir", extra={"job_id": job_id})
    raise NotImplementedError("Job temp cleanup pending Phase 5.")
