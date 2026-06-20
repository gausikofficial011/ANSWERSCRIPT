"""
application/use_cases/students/delete_student_use_case.py — Delete Student Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.student_repository import StudentRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException
from app.core.constants import AuditAction, AuditStatus


class DeleteStudentUseCase:
    def __init__(self, student_repo: StudentRepository, audit_repo: AuditLogRepository):
        self.student_repo = student_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        student_id: uuid.UUID,
        deleter_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> bool:
        student = await self.student_repo.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundException(entity_type="Student", entity_id=student_id)

        deleted = await self.student_repo.delete(student_id)
        if not deleted:
            return False

        # Log audit
        success_log = AuditLog(
            action=AuditAction.STUDENT_DELETED,
            resource_type="students",
            resource_id=student_id,
            status=AuditStatus.SUCCESS,
            user_id=deleter_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)
        return True
