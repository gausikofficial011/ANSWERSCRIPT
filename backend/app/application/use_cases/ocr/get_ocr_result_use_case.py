"""
application/use_cases/ocr/get_ocr_result_use_case.py — Get OCR Results Use Case
"""

from __future__ import annotations

import uuid

from app.domain.entities.ocr_result import OCRResult
from app.domain.repositories.ocr_result_repository import OCRResultRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException


class GetOCRResultUseCase:
    """
    Use case to fetch the page-wise OCR results for a specific answer sheet.
    """

    def __init__(
        self,
        answer_sheet_repo: AnswerSheetRepository,
        ocr_result_repo: OCRResultRepository
    ):
        self.answer_sheet_repo = answer_sheet_repo
        self.ocr_result_repo = ocr_result_repo

    async def execute(self, answer_sheet_id: uuid.UUID) -> list[OCRResult]:
        """
        Retrieves all OCRResults for the answer sheet, ordered by page number.

        Args:
            answer_sheet_id: UUID of the AnswerSheet.
        """
        sheet = await self.answer_sheet_repo.get_by_id(answer_sheet_id)
        if not sheet:
            raise EntityNotFoundException(entity_type="AnswerSheet", entity_id=answer_sheet_id)

        return await self.ocr_result_repo.list_by_answer_sheet_id(answer_sheet_id)
