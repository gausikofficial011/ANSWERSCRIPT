"""
application/use_cases/exams/update_exam_use_case.py — Update Exam Use Case
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from app.domain.entities.exam import Exam
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.subject_repository import SubjectRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException
from app.core.constants import ExamStatus, AuditAction, AuditStatus


class UpdateExamUseCase:
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
        exam_id: uuid.UUID,
        updater_id: uuid.UUID,
        title: str | None = None,
        description: str | None = None,
        exam_date: date | None = None,
        total_marks: int | None = None,
        passing_marks: int | None = None,
        duration_minutes: int | None = None,
        status: ExamStatus | None = None,
        scoring_config: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> Exam:
        exam = await self.exam_repo.get_by_id(exam_id)
        if exam is None:
            raise EntityNotFoundException(entity_type="Exam", entity_id=exam_id)

        old_values = {
            "title": exam.title,
            "description": exam.description,
            "exam_date": str(exam.exam_date),
            "total_marks": exam.total_marks,
            "passing_marks": exam.passing_marks,
            "duration_minutes": exam.duration_minutes,
            "status": exam.status.value if isinstance(exam.status, ExamStatus) else str(exam.status),
            "scoring_config": exam.scoring_config
        }

        # Validate marks invariants
        t_marks = total_marks if total_marks is not None else exam.total_marks
        p_marks = passing_marks if passing_marks is not None else exam.passing_marks

        if t_marks <= 0:
            raise BusinessRuleViolationException(rule="total_marks must be greater than 0.")
        if p_marks <= 0:
            raise BusinessRuleViolationException(rule="passing_marks must be greater than 0.")
        if p_marks > t_marks:
            raise BusinessRuleViolationException(rule="passing_marks cannot exceed total_marks.")

        if title is not None:
            exam.title = title.strip()
        if description is not None:
            exam.description = description.strip()
        if exam_date is not None:
            exam.exam_date = exam_date
        if total_marks is not None:
            exam.total_marks = total_marks
        if passing_marks is not None:
            exam.passing_marks = passing_marks
        if duration_minutes is not None:
            exam.duration_minutes = duration_minutes
        if status is not None:
            exam.status = status
        if scoring_config is not None:
            exam.scoring_config = scoring_config

        exam.updated_at = datetime.now(timezone.utc)

        new_values = {
            "title": exam.title,
            "description": exam.description,
            "exam_date": str(exam.exam_date),
            "total_marks": exam.total_marks,
            "passing_marks": exam.passing_marks,
            "duration_minutes": exam.duration_minutes,
            "status": exam.status.value if isinstance(exam.status, ExamStatus) else str(exam.status),
            "scoring_config": exam.scoring_config
        }

        saved = await self.exam_repo.save(exam)

        # Audit log
        success_log = AuditLog(
            action=AuditAction.EXAM_UPDATED,
            resource_type="exams",
            resource_id=exam_id,
            status=AuditStatus.SUCCESS,
            user_id=updater_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return saved
