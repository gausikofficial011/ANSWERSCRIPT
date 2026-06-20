"""
domain/entities/final_result.py — FinalResult Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid
from app.core.constants import PassFailStatus


@dataclass
class FinalResult:
    answer_sheet_id: uuid.UUID
    student_id: uuid.UUID
    exam_id: uuid.UUID
    total_marks_obtained: float
    total_marks_possible: int
    percentage: float
    pass_fail_status: PassFailStatus
    grade: str | None = None
    is_published: bool = False
    published_at: datetime | None = None
    published_by: uuid.UUID | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
