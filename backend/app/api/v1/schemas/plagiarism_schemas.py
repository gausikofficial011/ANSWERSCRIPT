"""
api/v1/schemas/plagiarism_schemas.py — Plagiarism Pydantic Schemas
"""

from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class PlagiarismSimilarityResponse(BaseModel):
    id: uuid.UUID
    source_answer_sheet_id: uuid.UUID
    target_answer_sheet_id: uuid.UUID
    source_question_mapping_id: uuid.UUID
    target_question_mapping_id: uuid.UUID
    semantic_similarity: float
    lexical_similarity: float
    overlap_similarity: float
    final_similarity: float
    risk_level: str
    created_at: datetime

    class Config:
        from_attributes = True


class PlagiarismReportResponse(BaseModel):
    id: uuid.UUID
    exam_id: uuid.UUID
    source_answer_sheet_id: uuid.UUID
    target_answer_sheet_id: uuid.UUID
    similarity_percentage: float
    highest_similarity: float
    risk_level: str
    similarity_details: dict | None = None
    flagged_questions: dict | None = None
    status: str
    reviewed_by: uuid.UUID | None = None
    reviewed_at: datetime | None = None
    teacher_notes: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlagiarismReviewRequest(BaseModel):
    status: str = Field(..., description="Review action, e.g. CONFIRMED_PLAGIARISM, FALSE_POSITIVE, DISMISSED")
    teacher_notes: str | None = Field(None, max_length=1000)
