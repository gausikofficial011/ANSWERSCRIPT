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

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from celery.utils.log import get_task_logger

from app.tasks.celery_app import celery_app
from app.config import get_settings
from app.infrastructure.reports.report_registry import report_registry

logger = get_task_logger(__name__)


REPORT_RETENTION_HOURS = 24


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
    deleted_count = 0
    freed_bytes = 0
    try:
        temp_dir = Path(get_settings().upload_dir) / "temporary"
        if temp_dir.exists() and temp_dir.is_dir():
            now = datetime.now()
            # 2 hours age limit
            limit = timedelta(hours=2)
            for root, _, files in os.walk(temp_dir):
                for f in files:
                    file_path = Path(root) / f
                    try:
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if now - mtime > limit:
                            size = file_path.stat().st_size
                            file_path.unlink()
                            deleted_count += 1
                            freed_bytes += size
                    except Exception as err:
                        logger.error(f"Failed to delete temp file {file_path}: {err}")
    except Exception as e:
        logger.error(f"Error during temporary files cleanup: {e}")
        
    logger.info(f"Cleanup: deleted {deleted_count} temp files, freed {freed_bytes} bytes")
    return {"deleted_count": deleted_count, "freed_bytes": freed_bytes}


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_expired_reports",
    queue="cleanup",
    max_retries=1,
    time_limit=600,
)
def cleanup_expired_reports() -> dict:
    """
    Periodic task: Remove expired entries from the ReportRegistry.
    Retention period = 24 hours.

    Returns:
        {"deleted_count": int, "freed_bytes": int}
    """
    logger.info("Cleanup: expired reports scan started")
    deleted_count = 0
    try:
        deleted_count = report_registry.remove_expired(retention_hours=REPORT_RETENTION_HOURS)
    except Exception as e:
        logger.error(f"Error during expired reports registry cleanup: {e}")
        
    logger.info(f"Cleanup: removed {deleted_count} expired report registry entries")
    return {"deleted_count": deleted_count, "freed_bytes": 0}


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
        {"job_id": str, "deleted_files": int, "deleted_directories": int}
    """
    logger.info("Cleanup: job temp dir", extra={"job_id": job_id})
    deleted_files = 0
    deleted_directories = 0
    try:
        job_temp_dir = Path(get_settings().upload_dir) / "temporary" / str(job_id)
        if job_temp_dir.exists() and job_temp_dir.is_dir():
            for root, dirs, files in os.walk(job_temp_dir, topdown=False):
                deleted_files += len(files)
                deleted_directories += len(dirs)
            deleted_directories += 1  # count the root job directory itself
            shutil.rmtree(job_temp_dir)
    except Exception as e:
        logger.error(f"Error cleaning up job temp dir for job {job_id}: {e}")
        
    return {
        "job_id": job_id, 
        "deleted_files": deleted_files, 
        "deleted_directories": deleted_directories
    }
