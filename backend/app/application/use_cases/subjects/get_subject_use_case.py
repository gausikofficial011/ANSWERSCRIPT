"""
application/use_cases/subjects/get_subject_use_case.py — Get Subject Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.subject import Subject
from app.domain.repositories.subject_repository import SubjectRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException


class GetSubjectUseCase:
    def __init__(self, subject_repo: SubjectRepository):
        self.subject_repo = subject_repo

    async def execute(self, subject_id: uuid.UUID) -> Subject:
        subject = await self.subject_repo.get_by_id(subject_id)
        if subject is None:
            raise EntityNotFoundException(entity_type="Subject", entity_id=subject_id)
        return subject
