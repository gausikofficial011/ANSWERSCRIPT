"""
domain/services/default_question_detector.py — Default Question Detector Implementation
"""

from __future__ import annotations

import re
from typing import Any
from uuid import UUID

from app.domain.entities.ocr_result import OCRResult
from app.domain.services.question_detector_interface import QuestionDetector


class DefaultQuestionDetector(QuestionDetector):
    """
    Concrete implementation of QuestionDetector.
    Scans bounding box text blocks for common question markers using regex.
    """

    def __init__(self, patterns: list[str] | None = None):
        if patterns is None:
            # Default regex patterns supporting: Q1, Q.1, Question 1, 1), 1., Ans 1, Answer 1
            patterns = [
                r'(?i)^\s*(?:question|answer|q|ans)\.?\s*(\d+)\b',
                r'^\s*(\d+)\s*[\).:]'
            ]
        self.patterns = [re.compile(p) for p in patterns]

    async def detect_questions(
        self,
        exam_id: UUID,
        ocr_results: list[OCRResult]
    ) -> list[dict[str, Any]]:
        """
        Detects question markers from page-wise OCR results.

        Args:
            exam_id: UUID of the exam.
            ocr_results: List of page-wise OCRResults.

        Returns:
            List of dictionaries representing detected question markers:
            [
                {
                    "detected_question_number": int,
                    "detected_question_label": str,
                    "block_index": int,     # index in flattened blocks
                    "page_number": int,
                    "block": dict
                }
            ]
        """
        # Flatten all bounding box blocks across pages
        flattened_blocks = []
        for ocr_res in ocr_results:
            # Sort blocks within page by y-coordinate then x-coordinate to ensure top-to-bottom reading order
            # (though EasyOCR usually handles this, sorting adds robustness)
            page_blocks = sorted(ocr_res.bounding_boxes, key=lambda b: (b.get("y1", 0), b.get("x1", 0)))
            for block in page_blocks:
                flattened_blocks.append({
                    "ocr_result_id": ocr_res.id,
                    "page_number": ocr_res.page_number,
                    "block": block
                })

        detected_markers = []
        for idx, item in enumerate(flattened_blocks):
            text = item["block"].get("text", "").strip()
            for pattern in self.patterns:
                match = pattern.search(text)
                if match:
                    # Extract the question number from the first capturing group
                    try:
                        q_num = int(match.group(1))
                        # Match label is the entire matched string (e.g. "Question 1")
                        q_label = match.group(0).strip()
                        
                        detected_markers.append({
                            "detected_question_number": q_num,
                            "detected_question_label": q_label,
                            "block_index": idx,
                            "page_number": item["page_number"],
                            "ocr_result_id": item["ocr_result_id"],
                            "block": item["block"]
                        })
                        # Found a match, break pattern search for this block
                        break
                    except (ValueError, IndexError):
                        continue

        return detected_markers
