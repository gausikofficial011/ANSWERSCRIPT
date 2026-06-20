"""
application/use_cases/model_answers/update_model_answer_use_case.py — Update ModelAnswer Use Case
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from app.domain.entities.model_answer import ModelAnswer
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.model_answer_repository import ModelAnswerRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException
from app.core.constants import AuditAction, AuditStatus


class UpdateModelAnswerUseCase:
    def __init__(self, model_answer_repo: ModelAnswerRepository, audit_repo: AuditLogRepository):
        self.model_answer_repo = model_answer_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        model_answer_id: uuid.UUID,
        updater_id: uuid.UUID,
        answer_text: str | None = None,
        keywords: list[str] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> ModelAnswer:
        model_ans = await self.model_answer_repo.get_by_id(model_answer_id)
        if model_ans is None:
            raise EntityNotFoundException(entity_type="ModelAnswer", entity_id=model_answer_id)

        old_values = {
            "answer_text": model_ans.answer_text,
            "keywords": model_ans.keywords
        }

        if answer_text is not None:
            model_ans.answer_text = answer_text.strip()
        if keywords is not None:
            model_ans.keywords = keywords

        model_ans.updated_at = datetime.now(timezone.utc)

        new_values = {
            "answer_text": model_ans.answer_text,
            "keywords": model_ans.keywords
        }

        saved = await self.model_answer_repo.save(model_ans)

        # Audit log
        success_log = AuditLog(
            action=AuditAction.MODEL_ANSWER_UPDATED,
            resource_type="model_answers",
            resource_id=model_answer_id,
            status=AuditStatus.SUCCESS,
            user_id=updater_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return saved
