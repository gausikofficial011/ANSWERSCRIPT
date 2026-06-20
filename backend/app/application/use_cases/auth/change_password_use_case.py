"""
application/use_cases/auth/change_password_use_case.py — Change Password Use Case

Handles changing a user's password securely: verifies the old password,
validates new password strength, updates password hash, revokes other sessions,
and audits the event.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import update

from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.value_objects.password import Password
from app.domain.exceptions.auth_exceptions import InvalidCredentialsException
from app.core.constants import AuditAction, AuditStatus
from app.infrastructure.auth.password_service import PasswordService


class ChangePasswordUseCase:
    """
    Use case for password modification.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        audit_repo: AuditLogRepository,
        session: any
    ):
        self.user_repo = user_repo
        self.audit_repo = audit_repo
        self.session = session

    async def execute(
        self,
        user_id: uuid.UUID,
        old_password: str,
        new_password: str,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise InvalidCredentialsException()

        # 1. Verify old password
        if not PasswordService.verify_password(old_password, user.hashed_password):
            # Log failed password change
            log = AuditLog(
                action=AuditAction.PASSWORD_CHANGED,
                resource_type="users",
                status=AuditStatus.FAILURE,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message="Old password verification failed."
            )
            await self.audit_repo.save(log)
            raise InvalidCredentialsException()

        # 2. Validate new password strength invariants (Domain Value Object)
        # This will raise ValueError if strength criteria are not met.
        Password(new_password)

        # 3. Hash new password
        new_hash = PasswordService.hash_password(new_password)

        # 4. Save new password hash
        user.hashed_password = new_hash
        await self.user_repo.save(user)

        # 5. Revoke all refresh tokens for this user
        if self.session:
            from app.infrastructure.persistence.models.refresh_token_model import RefreshTokenModel
            stmt = (
                update(RefreshTokenModel)
                .where(RefreshTokenModel.user_id == user_id)
                .values(is_revoked=True, updated_at=datetime.now(timezone.utc))
            )
            await self.session.execute(stmt)

        # 6. Log success
        log = AuditLog(
            action=AuditAction.PASSWORD_CHANGED,
            resource_type="users",
            status=AuditStatus.SUCCESS,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(log)
        return True
