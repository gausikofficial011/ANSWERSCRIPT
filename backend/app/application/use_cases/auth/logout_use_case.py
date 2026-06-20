"""
application/use_cases/auth/logout_use_case.py — Logout Use Case

Revokes an active refresh token session, invalidating it in the database
and logging a security logout audit trail.
"""

from __future__ import annotations

import uuid
from sqlalchemy import update, select

from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.core.constants import AuditAction, AuditStatus
from app.infrastructure.auth.jwt_service import JWTService


class LogoutUseCase:
    """
    Use case for logging out a user.
    """

    def __init__(self, audit_repo: AuditLogRepository, session: any):
        self.audit_repo = audit_repo
        self.session = session

    async def execute(
        self,
        refresh_token: str,
        user_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> bool:
        # 1. Hash token to lookup in database
        token_hash = JWTService.hash_token(refresh_token)

        if self.session:
            # Query token model
            from app.infrastructure.persistence.models.refresh_token_model import RefreshTokenModel
            stmt = (
                update(RefreshTokenModel)
                .where(
                    RefreshTokenModel.token_hash == token_hash,
                    RefreshTokenModel.user_id == user_id
                )
                .values(is_revoked=True, updated_at=func_now_helper())
            )
            await self.session.execute(stmt)

        # 2. Record Audit Event
        log = AuditLog(
            action=AuditAction.LOGOUT,
            resource_type="users",
            status=AuditStatus.SUCCESS,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(log)
        return True


def func_now_helper():
    from sqlalchemy import func
    return func.now()
