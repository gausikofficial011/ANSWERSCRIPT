"""
application/use_cases/ocr/get_question_mappings_use_case.py — Get Question Mappings Use Case
"""

from __future__ import annotations

import uuid

from app.domain.entities.question_mapping import QuestionMapping
from app.domain.repositories.question_mapping_repository import QuestionMappingRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException


class GetQuestionMappingsUseCase:
    """
    Retrieves the list of QuestionMapping entities for a specific answer sheet.
    """

    def __init__(
        self,
        answer_sheet_repo: AnswerSheetRepository,
        question_mapping_repo: QuestionMappingRepository
    ):
        self.answer_sheet_repo = answer_sheet_repo
        self.question_mapping_repo = question_mapping_repo

    async def execute(self, answer_sheet_id: uuid.UUID) -> list[QuestionMapping]:
        """
        Fetches all mappings ordered by question number.
        """
        sheet = await self.answer_sheet_repo.get_by_id(answer_sheet_id)
        if not sheet:
            raise EntityNotFoundException(entity_type="AnswerSheet", entity_id=answer_sheet_id)

        return await self.question_mapping_repo.list_by_answer_sheet_id(answer_sheet_id)
