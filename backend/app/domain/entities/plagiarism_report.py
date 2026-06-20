"""
domain/entities/plagiarism_report.py — PlagiarismReport Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid
from app.core.constants import PlagiarismStatus


@dataclass
class PlagiarismReport:
    exam_id: uuid.UUID
    source_answer_sheet_id: uuid.UUID
    target_answer_sheet_id: uuid.UUID
    similarity_percentage: float
    highest_similarity: float
    risk_level: str  # 'CLEAN', 'SUSPICIOUS', 'HIGH_RISK'
    similarity_details: dict | None = None
    flagged_questions: dict | None = None
    status: PlagiarismStatus = PlagiarismStatus.DETECTED
    reviewed_by: uuid.UUID | None = None
    reviewed_at: datetime | None = None
    teacher_notes: str | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
