"""
application/use_cases/exams/create_exam_use_case.py — Create Exam Use Case
"""

from __future__ import annotations

import uuid
from datetime import date
from app.domain.entities.exam import Exam
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.subject_repository import SubjectRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException
from app.core.constants import ExamStatus, AuditAction, AuditStatus


class CreateExamUseCase:
    def __init__(
        self,
        exam_repo: ExamRepository,
        subject_repo: SubjectRepository,
        audit_repo: AuditLogRepository
    ):
        self.exam_repo = exam_repo
        self.subject_repo = subject_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        subject_id: uuid.UUID,
        title: str,
        exam_date: date,
        total_marks: int,
        passing_marks: int,
        created_by: uuid.UUID,
        description: str | None = None,
        duration_minutes: int | None = None,
        status: ExamStatus = ExamStatus.DRAFT,
        scoring_config: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> Exam:
        # Validate subject exists
        subject = await self.subject_repo.get_by_id(subject_id)
        if subject is None:
            raise EntityNotFoundException(entity_type="Subject", entity_id=subject_id)

        # Enforce marks invariants
        if total_marks <= 0:
            raise BusinessRuleViolationException(rule="total_marks must be greater than 0.")
        if passing_marks <= 0:
            raise BusinessRuleViolationException(rule="passing_marks must be greater than 0.")
        if passing_marks > total_marks:
            raise BusinessRuleViolationException(rule="passing_marks cannot exceed total_marks.")

        exam = Exam(
            subject_id=subject_id,
            title=title.strip(),
            exam_date=exam_date,
            total_marks=total_marks,
            passing_marks=passing_marks,
            created_by=created_by,
            description=description.strip() if description else None,
            duration_minutes=duration_minutes,
            status=status,
            scoring_config=scoring_config or {}
        )

        saved = await self.exam_repo.save(exam)

        # Success audit log
        success_log = AuditLog(
            action=AuditAction.EXAM_CREATED,
            resource_type="exams",
            resource_id=saved.id,
            status=AuditStatus.SUCCESS,
            user_id=created_by,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return saved
