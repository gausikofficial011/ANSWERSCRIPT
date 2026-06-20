"""
api/v1/schemas/model_answer_schemas.py — ModelAnswer Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ModelAnswerCreateRequest(BaseModel):
    question_id: uuid.UUID = Field(..., description="Parent question foreign key")
    answer_text: str = Field(..., min_length=2, description="The correct/ideal solution text")
    keywords: list[str] = Field(default_factory=list, description="Expected matching keywords/phrases")


class ModelAnswerUpdateRequest(BaseModel):
    answer_text: str | None = Field(None, min_length=2)
    keywords: list[str] | None = None


class ModelAnswerResponse(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    answer_text: str
    keywords: list[str]
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
