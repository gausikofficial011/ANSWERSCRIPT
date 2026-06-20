"""
application/use_cases/model_answers/create_model_answer_use_case.py — Create ModelAnswer Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.model_answer import ModelAnswer
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.model_answer_repository import ModelAnswerRepository
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException, DuplicateEntityException
from app.core.constants import AuditAction, AuditStatus


class CreateModelAnswerUseCase:
    def __init__(
        self,
        model_answer_repo: ModelAnswerRepository,
        question_repo: QuestionRepository,
        audit_repo: AuditLogRepository
    ):
        self.model_answer_repo = model_answer_repo
        self.question_repo = question_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        question_id: uuid.UUID,
        answer_text: str,
        created_by: uuid.UUID,
        keywords: list[str] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> ModelAnswer:
        # Validate question exists
        question = await self.question_repo.get_by_id(question_id)
        if question is None:
            raise EntityNotFoundException(entity_type="Question", entity_id=question_id)

        # Enforce one model answer per question constraint
        existing = await self.model_answer_repo.get_by_question_id(question_id)
        if existing:
            fail_log = AuditLog(
                action=AuditAction.MODEL_ANSWER_CREATED,
                resource_type="model_answers",
                status=AuditStatus.FAILURE,
                user_id=created_by,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message=f"Model answer already exists for question '{question_id}'"
            )
            await self.audit_repo.save(fail_log)
            raise DuplicateEntityException(entity_type="ModelAnswer", field="question_id", value=str(question_id))

        model_ans = ModelAnswer(
            question_id=question_id,
            answer_text=answer_text.strip(),
            created_by=created_by,
            keywords=keywords or []
        )

        saved = await self.model_answer_repo.save(model_ans)

        # Success audit log
        success_log = AuditLog(
            action=AuditAction.MODEL_ANSWER_CREATED,
            resource_type="model_answers",
            resource_id=saved.id,
            status=AuditStatus.SUCCESS,
            user_id=created_by,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return saved
