"""
application/use_cases/model_answers/delete_model_answer_use_case.py — Delete ModelAnswer Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.model_answer_repository import ModelAnswerRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException
from app.core.constants import AuditAction, AuditStatus


class DeleteModelAnswerUseCase:
    def __init__(self, model_answer_repo: ModelAnswerRepository, audit_repo: AuditLogRepository):
        self.model_answer_repo = model_answer_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        model_answer_id: uuid.UUID,
        deleter_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> bool:
        model_ans = await self.model_answer_repo.get_by_id(model_answer_id)
        if model_ans is None:
            raise EntityNotFoundException(entity_type="ModelAnswer", entity_id=model_answer_id)

        deleted = await self.model_answer_repo.delete(model_answer_id)
        if not deleted:
            return False

        # Log audit
        success_log = AuditLog(
            action=AuditAction.MODEL_ANSWER_DELETED,
            resource_type="model_answers",
            resource_id=model_answer_id,
            status=AuditStatus.SUCCESS,
            user_id=deleter_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)
        return True
