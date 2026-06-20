"""
api/v1/schemas/exam_schemas.py — Exam Schemas
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator
from app.core.constants import ExamStatus


class ExamCreateRequest(BaseModel):
    subject_id: uuid.UUID = Field(..., description="Subject code foreign key")
    title: str = Field(..., min_length=2, max_length=255, description="Exam title")
    description: str | None = Field(None, description="Optional detailed overview")
    exam_date: date = Field(..., description="Scheduled exam date")
    total_marks: int = Field(..., description="Maximum reachable exam marks")
    passing_marks: int = Field(..., description="Minimum passing marks threshold")
    duration_minutes: int | None = Field(None, description="Optional exam duration time limits")
    status: ExamStatus = Field(ExamStatus.DRAFT, description="Draft, active, closed, or archived status")
    scoring_config: dict = Field(default_factory=dict, description="Custom weights and parameter config")

    @model_validator(mode="after")
    def validate_marks(self) -> ExamCreateRequest:
        if self.total_marks <= 0:
            raise ValueError("total_marks must be greater than 0.")
        if self.passing_marks <= 0:
            raise ValueError("passing_marks must be greater than 0.")
        if self.passing_marks > self.total_marks:
            raise ValueError("passing_marks cannot exceed total_marks.")
        return self


class ExamUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    exam_date: date | None = None
    total_marks: int | None = None
    passing_marks: int | None = None
    duration_minutes: int | None = None
    status: ExamStatus | None = None
    scoring_config: dict | None = None

    @model_validator(mode="after")
    def validate_marks(self) -> ExamUpdateRequest:
        t_marks = self.total_marks
        p_marks = self.passing_marks
        
        # We only validate if at least one is provided, otherwise we trust DB holds valid state
        if t_marks is not None and t_marks <= 0:
            raise ValueError("total_marks must be greater than 0.")
        if p_marks is not None and p_marks <= 0:
            raise ValueError("passing_marks must be greater than 0.")
            
        if t_marks is not None and p_marks is not None:
            if p_marks > t_marks:
                raise ValueError("passing_marks cannot exceed total_marks.")
        return self


class ExamResponse(BaseModel):
    id: uuid.UUID
    subject_id: uuid.UUID
    title: str
    description: str | None
    exam_date: date
    total_marks: int
    passing_marks: int
    duration_minutes: int | None
    status: ExamStatus
    scoring_config: dict
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
