"""
domain/entities/exam.py — Exam Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
import uuid
from app.core.constants import ExamStatus


@dataclass
class Exam:
    subject_id: uuid.UUID
    title: str
    exam_date: date
    total_marks: int
    passing_marks: int
    created_by: uuid.UUID
    description: str | None = None
    duration_minutes: int | None = None
    status: ExamStatus = ExamStatus.DRAFT
    scoring_config: dict = field(default_factory=dict)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    deleted_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
