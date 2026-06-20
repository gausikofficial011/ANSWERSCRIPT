"""
application/use_cases/students/list_students_use_case.py — List Students Use Case
"""

from __future__ import annotations

from app.domain.entities.student import Student
from app.domain.repositories.student_repository import StudentRepository
from app.core.pagination import PaginationParams, PaginatedResponse


class ListStudentsUseCase:
    def __init__(self, student_repo: StudentRepository):
        self.student_repo = student_repo

    async def execute(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        class_section: str | None = None
    ) -> PaginatedResponse[Student]:
        return await self.student_repo.list_students(
            pagination=pagination,
            search=search,
            class_section=class_section
        )
