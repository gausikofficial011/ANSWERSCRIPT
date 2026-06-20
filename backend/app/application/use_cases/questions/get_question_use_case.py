"""
application/use_cases/questions/get_question_use_case.py — Get Question Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.question import Question
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException


class GetQuestionUseCase:
    def __init__(self, question_repo: QuestionRepository):
        self.question_repo = question_repo

    async def execute(self, question_id: uuid.UUID) -> Question:
        question = await self.question_repo.get_by_id(question_id)
        if question is None:
            raise EntityNotFoundException(entity_type="Question", entity_id=question_id)
        return question
