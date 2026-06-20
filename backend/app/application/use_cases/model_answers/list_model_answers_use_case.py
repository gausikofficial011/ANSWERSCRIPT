"""
application/use_cases/model_answers/list_model_answers_use_case.py — List ModelAnswers Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.model_answer import ModelAnswer
from app.domain.repositories.model_answer_repository import ModelAnswerRepository
from app.core.pagination import PaginationParams, PaginatedResponse


class ListModelAnswersUseCase:
    def __init__(self, model_answer_repo: ModelAnswerRepository):
        self.model_answer_repo = model_answer_repo

    async def execute(
        self,
        pagination: PaginationParams,
        question_id: uuid.UUID | None = None
    ) -> PaginatedResponse[ModelAnswer]:
        return await self.model_answer_repo.list_model_answers(
            pagination=pagination,
            question_id=question_id
        )
