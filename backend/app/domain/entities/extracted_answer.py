"""
domain/entities/extracted_answer.py — ExtractedAnswer Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class ExtractedAnswer:
    ocr_result_id: uuid.UUID
    question_id: uuid.UUID
    answer_sheet_id: uuid.UUID
    extracted_text: str
    detected_question_number: int | None = None
    extraction_confidence: float | None = None
    page_number: int | None = None
    bounding_box: dict | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
