"""
domain/services/question_detector_interface.py — Abstract Question Detector Interface
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.domain.entities.ocr_result import OCRResult


class QuestionDetector(ABC):
    """
    Abstract contract for detecting questions or question boundaries within
    the extracted OCR results (text and coordinates).
    """

    @abstractmethod
    async def detect_questions(
        self,
        exam_id: UUID,
        ocr_results: list[OCRResult]
    ) -> list[dict[str, Any]]:
        """
        Detects question blocks and their associated bounding box areas.

        Args:
            exam_id: The ID of the exam.
            ocr_results: The list of page-wise OCR results containing bounding boxes.

        Returns:
            A list of dictionary definitions containing detected questions (e.g., question_number, coordinates).
        """
        ...
