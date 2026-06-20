"""
tests/unit/application/test_answer_segmentation.py — Unit Tests for Answer Segmentation
"""

from __future__ import annotations

import uuid
import pytest

from app.domain.entities.ocr_result import OCRResult
from app.domain.services.default_answer_segmenter import DefaultAnswerSegmenter
from app.core.constants import OCRResultStatus


@pytest.mark.asyncio
async def test_answer_segmentation():
    sheet_id = uuid.uuid4()
    ocr_1_id = uuid.uuid4()
    ocr_2_id = uuid.uuid4()

    ocr_results = [
        OCRResult(
            id=ocr_1_id,
            answer_sheet_id=sheet_id,
            page_number=1,
            extracted_text="Q1 Answer starts here. More answer text.",
            bounding_boxes=[
                {"text": "Q1: ", "confidence": 0.95, "x1": 10, "y1": 20, "x2": 40, "y2": 40},
                {"text": "Answer starts here.", "confidence": 0.95, "x1": 50, "y1": 20, "x2": 150, "y2": 40},
                {"text": "More answer text.", "confidence": 0.95, "x1": 50, "y1": 50, "x2": 150, "y2": 70}
            ],
            low_confidence_flag=False,
            confidence_score=0.95,
            average_confidence=0.95,
            words_detected=3,
            processing_time=0.2,
            ocr_engine_version="easyocr-1.0",
            preprocessing_version="opencv-1.0",
            original_image_path="",
            processed_image_path="",
            status=OCRResultStatus.OCR_COMPLETED
        ),
        OCRResult(
            id=ocr_2_id,
            answer_sheet_id=sheet_id,
            page_number=2,
            extracted_text="Answer continues on page 2. Q2 Second answer.",
            bounding_boxes=[
                {"text": "Answer continues on page 2.", "confidence": 0.90, "x1": 10, "y1": 20, "x2": 200, "y2": 40},
                {"text": "Q2: ", "confidence": 0.95, "x1": 10, "y1": 50, "x2": 40, "y2": 70},
                {"text": "Second answer.", "confidence": 0.95, "x1": 50, "y1": 50, "x2": 150, "y2": 70}
            ],
            low_confidence_flag=False,
            confidence_score=0.93,
            average_confidence=0.93,
            words_detected=3,
            processing_time=0.2,
            ocr_engine_version="easyocr-1.0",
            preprocessing_version="opencv-1.0",
            original_image_path="",
            processed_image_path="",
            status=OCRResultStatus.OCR_COMPLETED
        )
    ]

    detected_markers = [
        {
            "detected_question_number": 1,
            "detected_question_label": "Q1:",
            "block_index": 0,
            "page_number": 1,
            "ocr_result_id": ocr_1_id,
            "block": {"text": "Q1: ", "confidence": 0.95, "x1": 10, "y1": 20, "x2": 40, "y2": 40}
        },
        {
            "detected_question_number": 2,
            "detected_question_label": "Q2:",
            "block_index": 4,
            "page_number": 2,
            "ocr_result_id": ocr_2_id,
            "block": {"text": "Q2: ", "confidence": 0.95, "x1": 10, "y1": 50, "x2": 40, "y2": 70}
        }
    ]

    segmenter = DefaultAnswerSegmenter()
    segments = await segmenter.segment_answers(sheet_id, detected_questions=detected_markers, ocr_results=ocr_results)

    assert len(segments) == 2

    # Segment 1 (Continues across pages 1 and 2)
    seg1 = segments[0]
    assert seg1["detected_question_number"] == 1
    assert "Answer starts here. More answer text. Answer continues on page 2." in seg1["extracted_answer_text"]
    assert seg1["start_page"] == 1
    assert seg1["end_page"] == 2
    assert ocr_1_id in seg1["source_ocr_result_ids"]
    assert ocr_2_id in seg1["source_ocr_result_ids"]
    assert seg1["answer_page_count"] == 2
    assert seg1["answer_word_count"] == 11  # "Answer starts here. More answer text. Answer continues on page 2."

    # Segment 2
    seg2 = segments[1]
    assert seg2["detected_question_number"] == 2
    assert seg2["extracted_answer_text"] == "Second answer."
    assert seg2["start_page"] == 2
    assert seg2["end_page"] == 2
    assert seg2["answer_page_count"] == 1
    assert seg2["answer_word_count"] == 2
