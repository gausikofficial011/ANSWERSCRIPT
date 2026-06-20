"""
application/use_cases/subjects/create_subject_use_case.py — Create Subject Use Case
"""

from __future__ import annotations

import uuid
from app.domain.entities.subject import Subject
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.subject_repository import SubjectRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import DuplicateEntityException
from app.core.constants import AuditAction, AuditStatus


class CreateSubjectUseCase:
    def __init__(self, subject_repo: SubjectRepository, audit_repo: AuditLogRepository):
        self.subject_repo = subject_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        name: str,
        code: str,
        created_by: uuid.UUID,
        description: str | None = None,
        language: str = "en",
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> Subject:
        # Check if code already exists
        if await self.subject_repo.get_by_code(code):
            # Log failure
            fail_log = AuditLog(
                action=AuditAction.SUBJECT_CREATED,
                resource_type="subjects",
                status=AuditStatus.FAILURE,
                user_id=created_by,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message=f"Duplicate subject code: '{code}'"
            )
            await self.audit_repo.save(fail_log)
            raise DuplicateEntityException(entity_type="Subject", field="code", value=code)

        # Create Subject entity
        subject = Subject(
            name=name.strip(),
            code=code.strip().upper(),
            description=description,
            language=language,
            created_by=created_by
        )

        saved = await self.subject_repo.save(subject)

        # Log success
        success_log = AuditLog(
            action=AuditAction.SUBJECT_CREATED,
            resource_type="subjects",
            resource_id=saved.id,
            status=AuditStatus.SUCCESS,
            user_id=created_by,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return saved
