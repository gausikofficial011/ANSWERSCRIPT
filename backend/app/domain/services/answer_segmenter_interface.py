"""
domain/services/answer_segmenter_interface.py — Abstract Answer Segmenter Interface
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.domain.entities.ocr_result import OCRResult


class AnswerSegmenter(ABC):
    """
    Abstract contract for segmenting answers from the answer sheet page images
    or OCR blocks based on detected question regions.
    """

    @abstractmethod
    async def segment_answers(
        self,
        answer_sheet_id: UUID,
        detected_questions: list[dict[str, Any]],
        ocr_results: list[OCRResult]
    ) -> list[dict[str, Any]]:
        """
        Segments answers for each question block.

        Args:
            answer_sheet_id: The ID of the answer sheet.
            detected_questions: List of detected questions with their boundaries.
            ocr_results: The list of page-wise OCR results.

        Returns:
            A list of dictionary definitions containing the segmented answers (e.g., question_id, raw text, bounding boxes).
        """
        ...
