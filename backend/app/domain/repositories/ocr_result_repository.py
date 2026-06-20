"""
domain/repositories/ocr_result_repository.py — OCRResult Repository Interface

Defines the abstract interface for OCRResult entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.entities.ocr_result import OCRResult
from app.domain.repositories.base_repository import BaseRepository


class OCRResultRepository(BaseRepository[OCRResult]):
    """
    Abstract repository for OCRResult entities.
    """

    @abstractmethod
    async def list_by_answer_sheet_id(self, answer_sheet_id: UUID) -> list[OCRResult]:
        """Retrieve all page-wise OCR results for a specific answer sheet."""
        ...

    @abstractmethod
    async def get_by_page(self, answer_sheet_id: UUID, page_number: int) -> OCRResult | None:
        """Retrieve OCR result for a specific page of an answer sheet."""
        ...

    @abstractmethod
    async def delete_by_answer_sheet_id(self, answer_sheet_id: UUID) -> bool:
        """Delete all OCR results associated with a specific answer sheet."""
        ...
