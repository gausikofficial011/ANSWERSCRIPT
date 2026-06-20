"""
api/v1/schemas/question_mapping_schemas.py — Question Mapping Response Schemas
"""

from __future__ import annotations

from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class QuestionMappingResponse(BaseModel):
    id: uuid.UUID
    answer_sheet_id: uuid.UUID
    question_id: uuid.UUID | None = None
    detected_question_number: int | None = None
    detected_question_label: str | None = None
    extracted_answer_text: str
    start_page: int | None = None
    end_page: int | None = None
    mapping_confidence: float
    status: str
    duplicate_question_flag: bool
    duplicate_group_id: uuid.UUID | None = None
    source_ocr_result_ids: list[uuid.UUID]
    source_bounding_boxes: list[dict]
    source_page_numbers: list[int]
    answer_word_count: int
    answer_character_count: int
    answer_page_count: int
    corrected_question_id: uuid.UUID | None = None
    corrected_by_user_id: uuid.UUID | None = None
    corrected_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionMappingSummaryResponse(BaseModel):
    total_questions: int = Field(..., description="Total questions defined in the exam.")
    mapped_questions: int = Field(..., description="Number of questions successfully mapped.")
    unmapped_questions: int = Field(..., description="Number of unmapped answer segments.")
    duplicate_questions: int = Field(..., description="Number of answer segments flagged as duplicates.")
    not_attempted_questions: int = Field(..., description="Number of questions in the exam not attempted.")
