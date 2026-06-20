"""
api/v1/schemas/question_schemas.py — Question Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.constants import QuestionType


class QuestionCreateRequest(BaseModel):
    exam_id: uuid.UUID = Field(..., description="Parent exam foreign key")
    question_number: int = Field(..., ge=1, description="Question number order in exam (starts at 1)")
    question_text: str = Field(..., min_length=2, description="The actual question text query description")
    marks: int = Field(..., ge=1, description="Assigned marks value for this question")
    question_type: QuestionType = Field(QuestionType.SHORT, description="Short, long, mcq, or descriptive type")
    language: str = Field("en", min_length=2, max_length=50, description="Question translation language (default en)")


class QuestionUpdateRequest(BaseModel):
    question_number: int | None = Field(None, ge=1)
    question_text: str | None = Field(None, min_length=2)
    marks: int | None = Field(None, ge=1)
    question_type: QuestionType | None = None
    language: str | None = Field(None, min_length=2, max_length=50)


class QuestionResponse(BaseModel):
    id: uuid.UUID
    exam_id: uuid.UUID
    question_number: int
    question_text: str
    marks: int
    question_type: QuestionType
    language: str
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
