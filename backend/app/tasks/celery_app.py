"""
tasks/celery_app.py — Celery Application Instance

Single source of truth for Celery configuration.
All task modules import the `celery_app` instance from here.

Queue Strategy:
  - Separate queues allow independent worker scaling:
      docker-compose scale celery_ocr_worker=3
      docker-compose scale celery_eval_worker=2
  - Priority: ocr > evaluation > plagiarism > reports > cleanup

Routing:
  Task names → queue assignments are defined in CELERY_TASK_ROUTES.
  Workers are started with -Q <queue_name> flag.
"""

from __future__ import annotations

from celery import Celery

from app.config import get_settings

settings = get_settings()


def create_celery_app() -> Celery:
    """
    Factory function to create and configure the Celery application.

    Returns:
        Configured Celery instance ready for use.
    """
    app = Celery(
        "ai_eval_system",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=[
            "app.tasks.ocr_tasks",
            "app.tasks.evaluation_tasks",
            "app.tasks.plagiarism_tasks",
            "app.tasks.report_tasks",
            "app.tasks.cleanup_tasks",
        ],
    )

    app.conf.update(
        # ── Serialization ────────────────────────────────────────────────
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        # ── Timezone ────────────────────────────────────────────────────
        timezone="UTC",
        enable_utc=True,
        # ── Task Behavior ────────────────────────────────────────────────
        task_acks_late=True,             # Acknowledge only after task completes
        task_reject_on_worker_lost=True, # Re-queue if worker dies mid-task
        task_track_started=True,         # Enable STARTED state visibility
        # ── Result Expiry ────────────────────────────────────────────────
        result_expires=86400,            # Keep results for 24 hours
        # ── Concurrency ──────────────────────────────────────────────────
        worker_prefetch_multiplier=1,    # One task at a time per worker (OCR/AI are heavy)
        # ── Queue Routing ────────────────────────────────────────────────
        task_queues={
            "default":    {"exchange": "default"},
            "ocr":        {"exchange": "ocr"},
            "evaluation": {"exchange": "evaluation"},
            "plagiarism": {"exchange": "plagiarism"},
            "reports":    {"exchange": "reports"},
            "cleanup":    {"exchange": "cleanup"},
        },
        task_default_queue="default",
        task_routes={
            "app.tasks.ocr_tasks.*":         {"queue": "ocr"},
            "app.tasks.evaluation_tasks.*":  {"queue": "evaluation"},
            "app.tasks.plagiarism_tasks.*":  {"queue": "plagiarism"},
            "app.tasks.report_tasks.*":      {"queue": "reports"},
            "app.tasks.cleanup_tasks.*":     {"queue": "cleanup"},
        },
        # ── Beat Schedule (Periodic Tasks) ────────────────────────────────
        beat_schedule={
            # Run temp file cleanup every 2 hours
            "cleanup-temp-files": {
                "task": "app.tasks.cleanup_tasks.cleanup_temporary_files",
                "schedule": 7200.0,  # seconds
            },
            # Run expired report cleanup daily at 2 AM UTC
            "cleanup-expired-reports": {
                "task": "app.tasks.cleanup_tasks.cleanup_expired_reports",
                "schedule": 86400.0,
            },
        },
    )

    return app


# ── Singleton Instance ────────────────────────────────────────────────────────
# Import this in all task modules: from app.tasks.celery_app import celery_app

celery_app: Celery = create_celery_app()
