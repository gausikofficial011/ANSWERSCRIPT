"""
application/use_cases/exams/get_exam_use_case.py — Get Exam Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.exam import Exam
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException


class GetExamUseCase:
    def __init__(self, exam_repo: ExamRepository):
        self.exam_repo = exam_repo

    async def execute(self, exam_id: uuid.UUID) -> Exam:
        exam = await self.exam_repo.get_by_id(exam_id)
        if exam is None:
            raise EntityNotFoundException(entity_type="Exam", entity_id=exam_id)
        return exam
