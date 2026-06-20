"""
application/use_cases/rubrics/get_rubric_use_case.py — Get Rubric Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.rubric import Rubric
from app.domain.repositories.rubric_repository import RubricRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException


class GetRubricUseCase:
    def __init__(self, rubric_repo: RubricRepository):
        self.rubric_repo = rubric_repo

    async def execute(self, rubric_id: uuid.UUID) -> Rubric:
        rubric = await self.rubric_repo.get_by_id(rubric_id)
        if rubric is None:
            raise EntityNotFoundException(entity_type="Rubric", entity_id=rubric_id)
        return rubric
