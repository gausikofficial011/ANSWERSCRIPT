"""
domain/entities/ocr_result.py — OCRResult Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from app.core.constants import OCRResultStatus


@dataclass
class OCRResult:
    answer_sheet_id: uuid.UUID
    page_number: int
    extracted_text: str
    bounding_boxes: list[dict]
    low_confidence_flag: bool
    confidence_score: float
    average_confidence: float
    words_detected: int
    processing_time: float
    ocr_engine_version: str
    preprocessing_version: str
    original_image_path: str
    processed_image_path: str
    status: OCRResultStatus
    language_detected: str | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
