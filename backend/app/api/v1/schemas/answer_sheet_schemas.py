"""
api/v1/schemas/answer_sheet_schemas.py — Answer Sheet Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.constants import AnswerSheetStatus
from app.api.v1.schemas.pagination_schemas import PaginatedSchemaResponse


class AnswerSheetResponse(BaseModel):
    id: uuid.UUID
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
    status: AnswerSheetStatus
    error_message: str | None = None
    processed_at: datetime | None = None
    supersedes_answer_sheet_id: uuid.UUID | None = None
    superseded_by_answer_sheet_id: uuid.UUID | None = None
    processing_status: AnswerSheetStatus
    queued_at: datetime | None = None
    processing_started_at: datetime | None = None
    processing_completed_at: datetime | None = None
    failure_reason: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnswerSheetListResponse(PaginatedSchemaResponse[AnswerSheetResponse]):
    """Paginated list envelope for answer sheets."""
    pass
