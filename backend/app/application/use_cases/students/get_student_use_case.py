"""
application/use_cases/students/get_student_use_case.py — Get Student Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.student import Student
from app.domain.repositories.student_repository import StudentRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException


class GetStudentUseCase:
    def __init__(self, student_repo: StudentRepository):
        self.student_repo = student_repo

    async def execute(self, student_id: uuid.UUID) -> Student:
        student = await self.student_repo.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundException(entity_type="Student", entity_id=student_id)
        return student
