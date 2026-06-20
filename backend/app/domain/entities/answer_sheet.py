"""
domain/entities/answer_sheet.py — AnswerSheet Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid
from app.core.constants import AnswerSheetStatus


@dataclass
class AnswerSheet:
    exam_id: uuid.UUID
    student_id: uuid.UUID
    uploaded_by: uuid.UUID
    original_filename: str
    stored_filename: str
    file_path: str
    file_size_bytes: int
    mime_type: str
    file_hash: str
    page_count: int | None = None
    status: AnswerSheetStatus = AnswerSheetStatus.UPLOADED
    error_message: str | None = None
    processed_at: datetime | None = None
    deleted_at: datetime | None = None
    supersedes_answer_sheet_id: uuid.UUID | None = None
    superseded_by_answer_sheet_id: uuid.UUID | None = None
    processing_status: AnswerSheetStatus = AnswerSheetStatus.UPLOADED
    queued_at: datetime | None = None
    processing_started_at: datetime | None = None
    processing_completed_at: datetime | None = None
    failure_reason: str | None = None
    plagiarism_flagged: bool = False
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
