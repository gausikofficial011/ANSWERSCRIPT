"""
api/v1/schemas/ocr_schemas.py — OCR Response Schemas
"""

from __future__ import annotations

from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class BoundingBoxSchema(BaseModel):
    text: str = Field(..., description="Text extracted from the bounding box.")
    confidence: float = Field(..., description="OCR engine confidence score (0.0 to 1.0).")
    x1: int = Field(..., description="Top-left corner x coordinate.")
    y1: int = Field(..., description="Top-left corner y coordinate.")
    x2: int = Field(..., description="Bottom-right corner x coordinate.")
    y2: int = Field(..., description="Bottom-right corner y coordinate.")
    page_number: int = Field(..., description="The page number where this block resides.")
    low_confidence_flag: bool = Field(..., description="Flagged if confidence is below threshold.")


class OCRResultResponse(BaseModel):
    id: uuid.UUID
    answer_sheet_id: uuid.UUID
    page_number: int
    extracted_text: str
    bounding_boxes: list[BoundingBoxSchema]
    low_confidence_flag: bool
    confidence_score: float
    average_confidence: float
    words_detected: int
    processing_time: float
    ocr_engine_version: str
    preprocessing_version: str
    original_image_path: str
    processed_image_path: str
    status: str
    language_detected: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
