"""
application/use_cases/students/create_student_use_case.py — Create Student Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.student import Student
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.student_repository import StudentRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import DuplicateEntityException
from app.core.constants import AuditAction, AuditStatus


class CreateStudentUseCase:
    def __init__(self, student_repo: StudentRepository, audit_repo: AuditLogRepository):
        self.student_repo = student_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        student_number: str,
        full_name: str,
        creator_id: uuid.UUID,
        email: str | None = None,
        class_section: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> Student:
        student_num = student_number.strip()
        
        # Verify student number unique
        if await self.student_repo.get_by_student_number(student_num):
            fail_log = AuditLog(
                action=AuditAction.STUDENT_CREATED,
                resource_type="students",
                status=AuditStatus.FAILURE,
                user_id=creator_id,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message=f"Duplicate student number: '{student_num}'"
            )
            await self.audit_repo.save(fail_log)
            raise DuplicateEntityException(entity_type="Student", field="student_number", value=student_num)

        # Verify email unique
        if email:
            email_normalized = email.strip().lower()
            if await self.student_repo.get_by_email(email_normalized):
                fail_log = AuditLog(
                    action=AuditAction.STUDENT_CREATED,
                    resource_type="students",
                    status=AuditStatus.FAILURE,
                    user_id=creator_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    error_message=f"Duplicate student email: '{email_normalized}'"
                )
                await self.audit_repo.save(fail_log)
                raise DuplicateEntityException(entity_type="Student", field="email", value=email_normalized)

        student = Student(
            student_number=student_num,
            full_name=full_name.strip(),
            email=email.strip().lower() if email else None,
            class_section=class_section.strip() if class_section else None
        )

        saved = await self.student_repo.save(student)

        # Success audit log
        success_log = AuditLog(
            action=AuditAction.STUDENT_CREATED,
            resource_type="students",
            resource_id=saved.id,
            status=AuditStatus.SUCCESS,
            user_id=creator_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return saved
