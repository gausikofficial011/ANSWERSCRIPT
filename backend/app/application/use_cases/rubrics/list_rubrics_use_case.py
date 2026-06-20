"""
application/use_cases/rubrics/list_rubrics_use_case.py — List Rubrics Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.rubric import Rubric
from app.domain.repositories.rubric_repository import RubricRepository
from app.core.pagination import PaginationParams, PaginatedResponse


class ListRubricsUseCase:
    def __init__(self, rubric_repo: RubricRepository):
        self.rubric_repo = rubric_repo

    async def execute(
        self,
        pagination: PaginationParams,
        question_id: uuid.UUID | None = None,
        is_active: bool | None = None
    ) -> PaginatedResponse[Rubric]:
        return await self.rubric_repo.list_rubrics(
            pagination=pagination,
            question_id=question_id,
            is_active=is_active
        )
