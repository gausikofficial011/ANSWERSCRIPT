"""
storage/lifecycle/retention_policy.py — File Retention Policy Definitions

Defines how long each category of file is retained before deletion.
All policies are data objects — no filesystem operations here.
Cleanup logic lives in cleanup_scheduler.py.

Policies (per architecture decisions):
  - Temporary files:    Deleted immediately after job completes/fails
  - Failed sheets:      Retained 30 days, then soft-deleted
  - Old reports:        Retained 1 year, then archived/deleted
  - OCR JSON files:     Never auto-deleted (audit purposes)
  - Page images:        Permanent (until answer sheet is deleted)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum


class FileCategory(str, Enum):
    """Categories of files managed by the lifecycle system."""
    ANSWER_SHEET = "answer_sheets"
    PROCESSED_IMAGE = "processed_images"
    OCR_RESULT = "ocr_results"
    TEMPORARY = "temporary"
    REPORT = "reports"


@dataclass(frozen=True)
class RetentionPolicy:
    """
    Retention policy for a specific file category.

    Attributes:
        category:           The file category this policy applies to.
        max_age:            Maximum age before deletion (None = permanent).
        delete_on_job_end:  If True, delete immediately when processing job ends.
        archive_before_delete: If True, archive to cold storage before deletion (future).
    """
    category: FileCategory
    max_age: timedelta | None
    delete_on_job_end: bool = False
    archive_before_delete: bool = False


# ── Defined Policies ──────────────────────────────────────────────────────────

RETENTION_POLICIES: dict[FileCategory, RetentionPolicy] = {
    FileCategory.ANSWER_SHEET: RetentionPolicy(
        category=FileCategory.ANSWER_SHEET,
        max_age=None,              # Permanent (teachers may need to re-process)
        delete_on_job_end=False,
    ),
    FileCategory.PROCESSED_IMAGE: RetentionPolicy(
        category=FileCategory.PROCESSED_IMAGE,
        max_age=None,              # Permanent (needed for re-evaluation)
        delete_on_job_end=False,
    ),
    FileCategory.OCR_RESULT: RetentionPolicy(
        category=FileCategory.OCR_RESULT,
        max_age=None,              # Never auto-deleted (audit trail)
        delete_on_job_end=False,
    ),
    FileCategory.TEMPORARY: RetentionPolicy(
        category=FileCategory.TEMPORARY,
        max_age=timedelta(hours=2),  # Safety net: 2hr max in case job crashes
        delete_on_job_end=True,      # Primary: delete when job finishes
    ),
    FileCategory.REPORT: RetentionPolicy(
        category=FileCategory.REPORT,
        max_age=timedelta(days=365),  # 1 year
        delete_on_job_end=False,
        archive_before_delete=True,   # Future: cold storage archiving
    ),
}
