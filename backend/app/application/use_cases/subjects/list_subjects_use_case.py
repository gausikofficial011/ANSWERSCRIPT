"""
application/use_cases/subjects/list_subjects_use_case.py — List Subjects Use Case
"""

from __future__ import annotations

from app.domain.entities.subject import Subject
from app.domain.repositories.subject_repository import SubjectRepository
from app.core.pagination import PaginationParams, PaginatedResponse


class ListSubjectsUseCase:
    def __init__(self, subject_repo: SubjectRepository):
        self.subject_repo = subject_repo

    async def execute(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        is_active: bool | None = None
    ) -> PaginatedResponse[Subject]:
        return await self.subject_repo.list_subjects(
            pagination=pagination,
            search=search,
            is_active=is_active
        )
