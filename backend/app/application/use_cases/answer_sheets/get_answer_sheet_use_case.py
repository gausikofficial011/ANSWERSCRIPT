"""
application/use_cases/answer_sheets/get_answer_sheet_use_case.py — Get Answer Sheet Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.answer_sheet import AnswerSheet
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException


class GetAnswerSheetUseCase:
    def __init__(self, answer_sheet_repo: AnswerSheetRepository):
        self.answer_sheet_repo = answer_sheet_repo

    async def execute(self, answer_sheet_id: uuid.UUID) -> AnswerSheet:
        sheet = await self.answer_sheet_repo.get_by_id(answer_sheet_id)
        if sheet is None:
            raise EntityNotFoundException(entity_type="AnswerSheet", entity_id=answer_sheet_id)
        return sheet
