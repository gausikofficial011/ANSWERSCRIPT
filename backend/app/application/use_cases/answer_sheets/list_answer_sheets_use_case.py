"""
application/use_cases/answer_sheets/list_answer_sheets_use_case.py — List Answer Sheets Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.answer_sheet import AnswerSheet
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.core.pagination import PaginationParams, PaginatedResponse


class ListAnswerSheetsUseCase:
    def __init__(self, answer_sheet_repo: AnswerSheetRepository):
        self.answer_sheet_repo = answer_sheet_repo

    async def execute(
        self,
        pagination: PaginationParams,
        exam_id: uuid.UUID | None = None,
        student_id: uuid.UUID | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> PaginatedResponse[AnswerSheet]:
        return await self.answer_sheet_repo.list_answer_sheets(
            pagination=pagination,
            exam_id=exam_id,
            student_id=student_id,
            status=status,
            search=search
        )
