"""
domain/entities/evaluation_revision.py — EvaluationRevision Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class EvaluationRevision:
    evaluation_id: uuid.UUID
    revision_number: int
    new_score: float
    reason: str
    changed_by: uuid.UUID
    previous_score: float | None = None
    previous_feedback: str | None = None
    new_feedback: str | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
