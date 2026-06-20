"""
application/use_cases/subjects/update_subject_use_case.py — Update Subject Use Case
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from app.domain.entities.subject import Subject
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.subject_repository import SubjectRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException, DuplicateEntityException
from app.core.constants import AuditAction, AuditStatus


class UpdateSubjectUseCase:
    def __init__(self, subject_repo: SubjectRepository, audit_repo: AuditLogRepository):
        self.subject_repo = subject_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        subject_id: uuid.UUID,
        updater_id: uuid.UUID,
        name: str | None = None,
        code: str | None = None,
        description: str | None = None,
        language: str | None = None,
        is_active: bool | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> Subject:
        subject = await self.subject_repo.get_by_id(subject_id)
        if subject is None:
            raise EntityNotFoundException(entity_type="Subject", entity_id=subject_id)

        old_values = {
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "language": subject.language,
            "is_active": subject.is_active
        }

        # Validate code uniqueness if changing
        if code is not None:
            code_upper = code.strip().upper()
            if code_upper != subject.code:
                if await self.subject_repo.get_by_code(code_upper):
                    fail_log = AuditLog(
                        action=AuditAction.SUBJECT_UPDATED,
                        resource_type="subjects",
                        resource_id=subject_id,
                        status=AuditStatus.FAILURE,
                        user_id=updater_id,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        error_message=f"Duplicate subject code: '{code_upper}'"
                    )
                    await self.audit_repo.save(fail_log)
                    raise DuplicateEntityException(entity_type="Subject", field="code", value=code_upper)
                subject.code = code_upper

        if name is not None:
            subject.name = name.strip()
        if description is not None:
            subject.description = description.strip()
        if language is not None:
            subject.language = language.strip()
        if is_active is not None:
            subject.is_active = is_active

        subject.updated_at = datetime.now(timezone.utc)

        new_values = {
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "language": subject.language,
            "is_active": subject.is_active
        }

        saved = await self.subject_repo.save(subject)

        # Log audit
        success_log = AuditLog(
            action=AuditAction.SUBJECT_UPDATED,
            resource_type="subjects",
            resource_id=subject_id,
            status=AuditStatus.SUCCESS,
            user_id=updater_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return saved
