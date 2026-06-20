"""
tests/unit/application/test_question_detection.py — Unit Tests for Question Detection
"""

from __future__ import annotations

import uuid
import pytest

from app.domain.entities.ocr_result import OCRResult
from app.domain.services.default_question_detector import DefaultQuestionDetector
from app.core.constants import OCRResultStatus


@pytest.mark.asyncio
async def test_question_detection_patterns():
    # Setup OCRResult pages containing different question marker blocks
    ocr_results = [
        OCRResult(
            id=uuid.uuid4(),
            answer_sheet_id=uuid.uuid4(),
            page_number=1,
            extracted_text="Q1 Answer text here.",
            bounding_boxes=[
                {"text": "Q1", "confidence": 0.95, "x1": 10, "y1": 20, "x2": 40, "y2": 40},
                {"text": "Answer text here.", "confidence": 0.95, "x1": 50, "y1": 20, "x2": 150, "y2": 40}
            ],
            low_confidence_flag=False,
            confidence_score=0.95,
            average_confidence=0.95,
            words_detected=2,
            processing_time=0.2,
            ocr_engine_version="easyocr-1.0",
            preprocessing_version="opencv-1.0",
            original_image_path="",
            processed_image_path="",
            status=OCRResultStatus.OCR_COMPLETED
        ),
        OCRResult(
            id=uuid.uuid4(),
            answer_sheet_id=uuid.uuid4(),
            page_number=2,
            extracted_text="Question 2: Some other answer.",
            bounding_boxes=[
                {"text": "Question 2: ", "confidence": 0.9, "x1": 10, "y1": 50, "x2": 90, "y2": 70},
                {"text": "Some other answer.", "confidence": 0.95, "x1": 100, "y1": 50, "x2": 250, "y2": 70}
            ],
            low_confidence_flag=False,
            confidence_score=0.92,
            average_confidence=0.92,
            words_detected=2,
            processing_time=0.2,
            ocr_engine_version="easyocr-1.0",
            preprocessing_version="opencv-1.0",
            original_image_path="",
            processed_image_path="",
            status=OCRResultStatus.OCR_COMPLETED
        ),
        OCRResult(
            id=uuid.uuid4(),
            answer_sheet_id=uuid.uuid4(),
            page_number=3,
            extracted_text="3) This is q3.",
            bounding_boxes=[
                {"text": "3)", "confidence": 0.88, "x1": 10, "y1": 80, "x2": 30, "y2": 100},
                {"text": "This is q3.", "confidence": 0.9, "x1": 40, "y1": 80, "x2": 120, "y2": 100}
            ],
            low_confidence_flag=False,
            confidence_score=0.89,
            average_confidence=0.89,
            words_detected=2,
            processing_time=0.2,
            ocr_engine_version="easyocr-1.0",
            preprocessing_version="opencv-1.0",
            original_image_path="",
            processed_image_path="",
            status=OCRResultStatus.OCR_COMPLETED
        )
    ]

    detector = DefaultQuestionDetector()
    markers = await detector.detect_questions(uuid.uuid4(), ocr_results)

    assert len(markers) == 3
    
    # Q1
    assert markers[0]["detected_question_number"] == 1
    assert markers[0]["detected_question_label"] == "Q1"
    assert markers[0]["page_number"] == 1

    # Question 2
    assert markers[1]["detected_question_number"] == 2
    assert markers[1]["detected_question_label"] == "Question 2"
    assert markers[1]["page_number"] == 2

    # 3)
    assert markers[2]["detected_question_number"] == 3
    assert markers[2]["detected_question_label"] == "3)"
    assert markers[2]["page_number"] == 3
