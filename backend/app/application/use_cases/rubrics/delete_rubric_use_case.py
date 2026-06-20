"""
application/use_cases/rubrics/delete_rubric_use_case.py — Delete Rubric Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.rubric_repository import RubricRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException
from app.core.constants import AuditAction, AuditStatus


class DeleteRubricUseCase:
    def __init__(self, rubric_repo: RubricRepository, audit_repo: AuditLogRepository):
        self.rubric_repo = rubric_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        rubric_id: uuid.UUID,
        deleter_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> bool:
        rubric = await self.rubric_repo.get_by_id(rubric_id)
        if rubric is None:
            raise EntityNotFoundException(entity_type="Rubric", entity_id=rubric_id)

        # Enforce lock invariant: cannot delete locked rubrics
        if rubric.is_locked:
            raise BusinessRuleViolationException(
                rule="Cannot delete a rubric that is currently locked (used in student evaluations)."
            )

        deleted = await self.rubric_repo.delete(rubric_id)
        if not deleted:
            return False

        # Log audit
        success_log = AuditLog(
            action=AuditAction.RUBRIC_DELETED,
            resource_type="rubrics",
            resource_id=rubric_id,
            status=AuditStatus.SUCCESS,
            user_id=deleter_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)
        return True
