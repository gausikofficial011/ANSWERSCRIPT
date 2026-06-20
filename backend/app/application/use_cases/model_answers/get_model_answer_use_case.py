"""
application/use_cases/model_answers/get_model_answer_use_case.py — Get ModelAnswer Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.model_answer import ModelAnswer
from app.domain.repositories.model_answer_repository import ModelAnswerRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException


class GetModelAnswerUseCase:
    def __init__(self, model_answer_repo: ModelAnswerRepository):
        self.model_answer_repo = model_answer_repo

    async def execute(self, model_answer_id: uuid.UUID) -> ModelAnswer:
        model_ans = await self.model_answer_repo.get_by_id(model_answer_id)
        if model_ans is None:
            raise EntityNotFoundException(entity_type="ModelAnswer", entity_id=model_answer_id)
        return model_ans
