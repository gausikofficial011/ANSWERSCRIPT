"""
application/use_cases/exams/delete_exam_use_case.py — Delete Exam Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException
from app.core.constants import AuditAction, AuditStatus


class DeleteExamUseCase:
    def __init__(self, exam_repo: ExamRepository, audit_repo: AuditLogRepository):
        self.exam_repo = exam_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        exam_id: uuid.UUID,
        deleter_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> bool:
        exam = await self.exam_repo.get_by_id(exam_id)
        if exam is None:
            raise EntityNotFoundException(entity_type="Exam", entity_id=exam_id)

        deleted = await self.exam_repo.delete(exam_id)
        if not deleted:
            return False

        # Log audit
        success_log = AuditLog(
            action=AuditAction.EXAM_DELETED,
            resource_type="exams",
            resource_id=exam_id,
            status=AuditStatus.SUCCESS,
            user_id=deleter_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)
        return True
