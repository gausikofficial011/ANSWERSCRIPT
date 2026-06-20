"""
application/use_cases/questions/create_question_use_case.py — Create Question Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.question import Question
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException, DuplicateEntityException
from app.core.constants import QuestionType, AuditAction, AuditStatus


class CreateQuestionUseCase:
    def __init__(
        self,
        question_repo: QuestionRepository,
        exam_repo: ExamRepository,
        audit_repo: AuditLogRepository
    ):
        self.question_repo = question_repo
        self.exam_repo = exam_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        exam_id: uuid.UUID,
        question_number: int,
        question_text: str,
        marks: int,
        question_type: QuestionType,
        created_by: uuid.UUID,
        language: str = "en",
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> Question:
        # Validate exam exists
        exam = await self.exam_repo.get_by_id(exam_id)
        if exam is None:
            raise EntityNotFoundException(entity_type="Exam", entity_id=exam_id)

        # Validate unique question number in exam
        if await self.question_repo.get_by_number(exam_id, question_number):
            fail_log = AuditLog(
                action=AuditAction.QUESTION_CREATED,
                resource_type="questions",
                status=AuditStatus.FAILURE,
                user_id=created_by,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message=f"Duplicate question number {question_number} in exam {exam_id}"
            )
            await self.audit_repo.save(fail_log)
            raise DuplicateEntityException(entity_type="Question", field="question_number", value=str(question_number))

        question = Question(
            exam_id=exam_id,
            question_number=question_number,
            question_text=question_text.strip(),
            marks=marks,
            question_type=question_type,
            created_by=created_by,
            language=language
        )

        saved = await self.question_repo.save(question)

        # Audit log
        success_log = AuditLog(
            action=AuditAction.QUESTION_CREATED,
            resource_type="questions",
            resource_id=saved.id,
            status=AuditStatus.SUCCESS,
            user_id=created_by,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return saved
