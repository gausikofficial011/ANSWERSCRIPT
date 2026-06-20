"""
domain/entities/model_answer.py — ModelAnswer Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class ModelAnswer:
    question_id: uuid.UUID
    answer_text: str
    created_by: uuid.UUID
    keywords: list[str] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    deleted_at: datetime | None = None

