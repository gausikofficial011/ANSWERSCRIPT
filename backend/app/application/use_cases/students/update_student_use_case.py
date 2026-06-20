"""
application/use_cases/students/update_student_use_case.py — Update Student Use Case
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from app.domain.entities.student import Student
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.student_repository import StudentRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException, DuplicateEntityException
from app.core.constants import AuditAction, AuditStatus


class UpdateStudentUseCase:
    def __init__(self, student_repo: StudentRepository, audit_repo: AuditLogRepository):
        self.subject_repo = student_repo  # Keep repository reference
        self.student_repo = student_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        student_id: uuid.UUID,
        updater_id: uuid.UUID,
        student_number: str | None = None,
        full_name: str | None = None,
        email: str | None = None,
        class_section: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> Student:
        student = await self.student_repo.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundException(entity_type="Student", entity_id=student_id)

        old_values = {
            "student_number": student.student_number,
            "full_name": student.full_name,
            "email": student.email,
            "class_section": student.class_section
        }

        # Validate unique student number if changing
        if student_number is not None:
            num_clean = student_number.strip()
            if num_clean != student.student_number:
                if await self.student_repo.get_by_student_number(num_clean):
                    fail_log = AuditLog(
                        action=AuditAction.STUDENT_UPDATED,
                        resource_type="students",
                        resource_id=student_id,
                        status=AuditStatus.FAILURE,
                        user_id=updater_id,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        error_message=f"Duplicate student number: '{num_clean}'"
                    )
                    await self.audit_repo.save(fail_log)
                    raise DuplicateEntityException(entity_type="Student", field="student_number", value=num_clean)
                student.student_number = num_clean

        # Validate unique email if changing
        if email is not None:
            email_clean = email.strip().lower() if email.strip() else None
            if email_clean != student.email and email_clean is not None:
                if await self.student_repo.get_by_email(email_clean):
                    fail_log = AuditLog(
                        action=AuditAction.STUDENT_UPDATED,
                        resource_type="students",
                        resource_id=student_id,
                        status=AuditStatus.FAILURE,
                        user_id=updater_id,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        error_message=f"Duplicate email: '{email_clean}'"
                    )
                    await self.audit_repo.save(fail_log)
                    raise DuplicateEntityException(entity_type="Student", field="email", value=email_clean)
            student.email = email_clean

        if full_name is not None:
            student.full_name = full_name.strip()
        if class_section is not None:
            student.class_section = class_section.strip() if class_section.strip() else None

        student.updated_at = datetime.now(timezone.utc)

        new_values = {
            "student_number": student.student_number,
            "full_name": student.full_name,
            "email": student.email,
            "class_section": student.class_section
        }

        saved = await self.student_repo.save(student)

        # Audit log
        success_log = AuditLog(
            action=AuditAction.STUDENT_UPDATED,
            resource_type="students",
            resource_id=student_id,
            status=AuditStatus.SUCCESS,
            user_id=updater_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return saved
