"""
application/use_cases/questions/list_questions_use_case.py — List Questions Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.question import Question
from app.domain.repositories.question_repository import QuestionRepository
from app.core.pagination import PaginationParams, PaginatedResponse


class ListQuestionsUseCase:
    def __init__(self, question_repo: QuestionRepository):
        self.question_repo = question_repo

    async def execute(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        exam_id: uuid.UUID | None = None
    ) -> PaginatedResponse[Question]:
        return await self.question_repo.list_questions(
            pagination=pagination,
            search=search,
            exam_id=exam_id
        )
