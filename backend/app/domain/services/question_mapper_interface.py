"""
domain/services/question_mapper_interface.py — Abstract Question Mapper Interface
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.domain.entities.ocr_result import OCRResult


class QuestionMapper(ABC):
    """
    Abstract contract for mapping segmented student answers to the actual
    Exam Questions and Model Answers defined in the academic catalog.
    """

    @abstractmethod
    async def map_segmented_answers_to_questions(
        self,
        exam_id: UUID,
        segmented_answers: list[dict[str, Any]],
        ocr_results: list[OCRResult]
    ) -> list[dict[str, Any]]:
        """
        Maps segmented answer blocks to specific exam question IDs.

        Args:
            exam_id: The ID of the exam.
            segmented_answers: List of segmented answers.
            ocr_results: The list of page-wise OCR results.

        Returns:
            A list of dictionary definitions containing mapping results (e.g., question_id, student_answer_text).
        """
        ...
