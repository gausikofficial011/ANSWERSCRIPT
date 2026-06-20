"""
application/use_cases/answer_sheets/delete_answer_sheet_use_case.py — Delete Answer Sheet Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException
from app.core.constants import AuditAction, AuditStatus


class DeleteAnswerSheetUseCase:
    def __init__(self, answer_sheet_repo: AnswerSheetRepository, audit_repo: AuditLogRepository):
        self.answer_sheet_repo = answer_sheet_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        answer_sheet_id: uuid.UUID,
        deleter_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> bool:
        sheet = await self.answer_sheet_repo.get_by_id(answer_sheet_id)
        if sheet is None:
            raise EntityNotFoundException(entity_type="AnswerSheet", entity_id=answer_sheet_id)

        deleted = await self.answer_sheet_repo.delete(answer_sheet_id)
        if not deleted:
            return False

        # Log audit
        success_log = AuditLog(
            action=AuditAction.ANSWER_SHEET_DELETED,
            resource_type="answer_sheets",
            resource_id=answer_sheet_id,
            status=AuditStatus.SUCCESS,
            user_id=deleter_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)
        return True
