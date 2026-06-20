"""
api/v1/schemas/student_schemas.py — Student Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class StudentCreateRequest(BaseModel):
    student_number: str = Field(..., min_length=2, max_length=50, description="Unique registration student identifier")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name of the student")
    email: str | None = Field(None, description="Optional student email address")
    class_section: str | None = Field(None, max_length=50, description="Class segment or batch section")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        from app.domain.value_objects.email import Email
        try:
            email_vo = Email(v)
            return str(email_vo)
        except ValueError as e:
            raise ValueError(str(e))


class StudentUpdateRequest(BaseModel):
    student_number: str | None = Field(None, min_length=2, max_length=50)
    full_name: str | None = Field(None, min_length=2, max_length=255)
    email: str | None = None
    class_section: str | None = Field(None, max_length=50)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        from app.domain.value_objects.email import Email
        try:
            email_vo = Email(v)
            return str(email_vo)
        except ValueError as e:
            raise ValueError(str(e))


class StudentResponse(BaseModel):
    id: uuid.UUID
    student_number: str
    full_name: str
    email: str | None
    class_section: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
