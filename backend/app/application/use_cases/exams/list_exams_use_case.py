"""
application/use_cases/exams/list_exams_use_case.py — List Exams Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.exam import Exam
from app.domain.repositories.exam_repository import ExamRepository
from app.core.pagination import PaginationParams, PaginatedResponse


class ListExamsUseCase:
    def __init__(self, exam_repo: ExamRepository):
        self.exam_repo = exam_repo

    async def execute(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        subject_id: uuid.UUID | None = None,
        status: str | None = None
    ) -> PaginatedResponse[Exam]:
        return await self.exam_repo.list_exams(
            pagination=pagination,
            search=search,
            subject_id=subject_id,
            status=status
        )
