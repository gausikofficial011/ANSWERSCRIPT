"""
application/use_cases/questions/update_question_use_case.py — Update Question Use Case
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from app.domain.entities.question import Question
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException, DuplicateEntityException
from app.core.constants import QuestionType, AuditAction, AuditStatus


class UpdateQuestionUseCase:
    def __init__(self, question_repo: QuestionRepository, audit_repo: AuditLogRepository):
        self.question_repo = question_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        question_id: uuid.UUID,
        updater_id: uuid.UUID,
        question_number: int | None = None,
        question_text: str | None = None,
        marks: int | None = None,
        question_type: QuestionType | None = None,
        language: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> Question:
        question = await self.question_repo.get_by_id(question_id)
        if question is None:
            raise EntityNotFoundException(entity_type="Question", entity_id=question_id)

        old_values = {
            "question_number": question.question_number,
            "question_text": question.question_text,
            "marks": question.marks,
            "question_type": question.question_type.value if isinstance(question.question_type, QuestionType) else str(question.question_type),
            "language": question.language
        }

        # Check unique question_number in exam
        if question_number is not None and question_number != question.question_number:
            existing = await self.question_repo.get_by_number(question.exam_id, question_number)
            if existing:
                fail_log = AuditLog(
                    action=AuditAction.QUESTION_UPDATED,
                    resource_type="questions",
                    resource_id=question_id,
                    status=AuditStatus.FAILURE,
                    user_id=updater_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    error_message=f"Duplicate question number {question_number} in exam {question.exam_id}"
                )
                await self.audit_repo.save(fail_log)
                raise DuplicateEntityException(entity_type="Question", field="question_number", value=str(question_number))
            question.question_number = question_number

        if question_text is not None:
            question.question_text = question_text.strip()
        if marks is not None:
            question.marks = marks
        if question_type is not None:
            question.question_type = question_type
        if language is not None:
            question.language = language.strip()

        question.updated_at = datetime.now(timezone.utc)

        new_values = {
            "question_number": question.question_number,
            "question_text": question.question_text,
            "marks": question.marks,
            "question_type": question.question_type.value if isinstance(question.question_type, QuestionType) else str(question.question_type),
            "language": question.language
        }

        saved = await self.question_repo.save(question)

        # Audit log
        success_log = AuditLog(
            action=AuditAction.QUESTION_UPDATED,
            resource_type="questions",
            resource_id=question_id,
            status=AuditStatus.SUCCESS,
            user_id=updater_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return saved
