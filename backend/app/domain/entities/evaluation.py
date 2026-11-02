"""
domain/entities/evaluation.py — Evaluation Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Evaluation:
    answer_sheet_id: uuid.UUID
    question_mapping_id: uuid.UUID
    question_id: uuid.UUID
    model_answer_id: uuid.UUID
    max_marks: int
    rubric_id: uuid.UUID | None = None
    ai_score: float | None = None
    similarity_score: float | None = None
    keyword_match_score: float | None = None
    ai_feedback: str | None = None
    teacher_score: float | None = None
    teacher_feedback: str | None = None
    is_verified: bool = False
    verified_by: uuid.UUID | None = None
    verified_at: datetime | None = None
    evaluation_model: str | None = None
    evaluation_confidence: float | None = None
    confidence_score: float | None = None
    low_confidence_flag: bool = False
    explanation: dict | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def final_score(self) -> float | None:
        """Resolved score: teacher override takes precedence over AI score."""
        return self.teacher_score if self.teacher_score is not None else self.ai_score

    @property
    def has_teacher_override(self) -> bool:
        return self.teacher_score is not None

