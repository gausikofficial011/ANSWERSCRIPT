"""
domain/entities/question.py — Question Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid
from app.core.constants import QuestionType


@dataclass
class Question:
    exam_id: uuid.UUID
    question_number: int
    question_text: str
    marks: int
    question_type: QuestionType
    created_by: uuid.UUID
    language: str = "en"
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    deleted_at: datetime | None = None

