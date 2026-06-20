"""
domain/entities/question_mapping.py — QuestionMapping Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class QuestionMapping:
    answer_sheet_id: uuid.UUID
    question_id: uuid.UUID | None
    detected_question_number: int | None
    detected_question_label: str | None
    extracted_answer_text: str
    start_page: int | None
    end_page: int | None
    mapping_confidence: float
    status: str
    duplicate_question_flag: bool = False
    duplicate_group_id: uuid.UUID | None = None
    source_ocr_result_ids: list[uuid.UUID] = field(default_factory=list)
    source_bounding_boxes: list[dict] = field(default_factory=list)
    source_page_numbers: list[int] = field(default_factory=list)
    answer_word_count: int = 0
    answer_character_count: int = 0
    answer_page_count: int = 0
    corrected_question_id: uuid.UUID | None = None
    corrected_by_user_id: uuid.UUID | None = None
    corrected_at: datetime | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
