"""
application/use_cases/questions/delete_question_use_case.py — Delete Question Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException
from app.core.constants import AuditAction, AuditStatus


class DeleteQuestionUseCase:
    def __init__(self, question_repo: QuestionRepository, audit_repo: AuditLogRepository):
        self.question_repo = question_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        question_id: uuid.UUID,
        deleter_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> bool:
        question = await self.question_repo.get_by_id(question_id)
        if question is None:
            raise EntityNotFoundException(entity_type="Question", entity_id=question_id)

        deleted = await self.question_repo.delete(question_id)
        if not deleted:
            return False

        # Log audit
        success_log = AuditLog(
            action=AuditAction.QUESTION_DELETED,
            resource_type="questions",
            resource_id=question_id,
            status=AuditStatus.SUCCESS,
            user_id=deleter_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)
        return True
