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


class ExtractedQuestionSchema(BaseModel):
    question_number: int = Field(..., description="Detected sequence or question number")
    question_text: str = Field(..., description="Extracted question prompt text")
    question_type: str = Field(default="ESSAY", description="Inferred question type: ESSAY, SHORT_ANSWER, or NUMERICAL")
    max_marks: int = Field(default=10, description="Detected or default maximum marks")
    suggested_keywords: list[str] = Field(default_factory=list, description="Extracted key concepts and lexical terms")
    suggested_model_answer: str | None = Field(default=None, description="Extracted or inferred benchmark answer text")


class DocumentPageExtractionSchema(BaseModel):
    page_number: int = Field(..., description="1-indexed document page number")
    text: str = Field(..., description="Extracted text on this page")
    confidence: float = Field(default=1.0, description="Confidence score from 0.0 to 1.0")
    method: str = Field(default="digital_pdf", description="Extraction technique used: digital_pdf or ocr_easyocr")
    bounding_boxes: list[BoundingBoxSchema] = Field(default_factory=list, description="Word or phrase bounding boxes")


class DocumentExtractionResponse(BaseModel):
    filename: str = Field(..., description="Original name of the uploaded document")
    file_type: str = Field(..., description="MIME type or file format")
    total_pages: int = Field(..., description="Number of pages processed")
    total_words: int = Field(..., description="Total word count extracted")
    average_confidence: float = Field(..., description="Average OCR or extraction confidence score")
    extraction_method: str = Field(..., description="Overall extraction pipeline used")
    extracted_full_text: str = Field(..., description="Concatenated extracted plain text")
    suggested_keywords: list[str] = Field(default_factory=list, description="Global extracted keywords")
    detected_questions: list[ExtractedQuestionSchema] = Field(default_factory=list, description="Structured parsed questions")
    pages: list[DocumentPageExtractionSchema] = Field(default_factory=list, description="Per-page extracted details")
