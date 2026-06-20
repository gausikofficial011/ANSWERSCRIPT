"""
api/v1/schemas/subject_schemas.py — Subject Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class SubjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Subject name")
    code: str = Field(..., min_length=2, max_length=50, description="Unique subject code (e.g. CS101)")
    description: str | None = Field(None, description="Optional detailed description")
    language: str = Field("en", min_length=2, max_length=50, description="Teaching language (default en)")


class SubjectUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    code: str | None = Field(None, min_length=2, max_length=50)
    description: str | None = None
    language: str | None = Field(None, min_length=2, max_length=50)
    is_active: bool | None = None


class SubjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    description: str | None
    language: str
    is_active: bool
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
