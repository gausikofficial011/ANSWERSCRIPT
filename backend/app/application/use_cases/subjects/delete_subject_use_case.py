"""
application/use_cases/subjects/delete_subject_use_case.py — Delete Subject Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.subject_repository import SubjectRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException
from app.core.constants import AuditAction, AuditStatus


class DeleteSubjectUseCase:
    def __init__(self, subject_repo: SubjectRepository, audit_repo: AuditLogRepository):
        self.subject_repo = subject_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        subject_id: uuid.UUID,
        deleter_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> bool:
        subject = await self.subject_repo.get_by_id(subject_id)
        if subject is None:
            raise EntityNotFoundException(entity_type="Subject", entity_id=subject_id)

        deleted = await self.subject_repo.delete(subject_id)
        if not deleted:
            return False

        # Log audit
        success_log = AuditLog(
            action=AuditAction.SUBJECT_DELETED,
            resource_type="subjects",
            resource_id=subject_id,
            status=AuditStatus.SUCCESS,
            user_id=deleter_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)
        return True
