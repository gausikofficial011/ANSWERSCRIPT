"""
application/use_cases/auth/login_use_case.py — Login Use Case

Handles authenticating a user by credentials, verifying password hashes,
generating access/refresh tokens, storing the session, and audit logging.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from typing import TypedDict

from app.domain.entities.audit_log import AuditLog
from app.domain.entities.refresh_token import RefreshToken
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.role_repository import RoleRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.auth_exceptions import (
    InvalidCredentialsException,
    AccountInactiveException
)
from app.core.constants import AuditAction, AuditStatus
from app.infrastructure.auth.password_service import PasswordService
from app.infrastructure.auth.jwt_service import JWTService
from app.config import get_settings

settings = get_settings()


class LoginResult(TypedDict):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: uuid.UUID
    username: str
    role: str


class LoginUseCase:
    """
    Use case for authenticating users.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        audit_repo: AuditLogRepository,
        # We pass database session to handle refresh token inserts since it's an infra action
        session: any = None
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.audit_repo = audit_repo
        self.session = session

    async def execute(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> LoginResult:
        # 1. Fetch user
        user = await self.user_repo.get_by_email(email)

        # Log failed login helper
        async def log_failure(reason: str, ref_user_id: uuid.UUID | None = None) -> None:
            log = AuditLog(
                action=AuditAction.LOGIN_FAILED,
                resource_type="users",
                status=AuditStatus.FAILURE,
                user_id=ref_user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message=reason
            )
            await self.audit_repo.save(log)

        if user is None:
            await log_failure("Email address not found.")
            raise InvalidCredentialsException()

        # 2. Verify password
        if not PasswordService.verify_password(password, user.hashed_password):
            await log_failure("Password mismatch.", user.id)
            raise InvalidCredentialsException()

        # 3. Check active state
        if not user.is_active:
            await log_failure("Account is inactive.", user.id)
            raise AccountInactiveException()

        # 4. Fetch Role Details
        role = await self.role_repo.get_by_id(user.role_id)
        role_name = role.name if role else "teacher"

        # 5. Generate tokens
        access_token = JWTService.create_access_token(user.id, user.username, role_name)
        refresh_token = JWTService.create_refresh_token(user.id)

        # 6. Save Refresh Token in Database (SHA-256 hashed)
        hashed_rt = JWTService.hash_token(refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
        
        # Save token via direct SQL insertion in the session
        if self.session:
            from app.infrastructure.persistence.models.refresh_token_model import RefreshTokenModel
            db_token = RefreshTokenModel(
                id=uuid.uuid4(),
                user_id=user.id,
                token_hash=hashed_rt,
                expires_at=expires_at,
                is_revoked=False
            )
            self.session.add(db_token)
            await self.session.flush()

        # 7. Update Last Login Timestamp
        await self.user_repo.update_last_login(user.id)

        # 8. Log Success
        success_log = AuditLog(
            action=AuditAction.LOGIN,
            resource_type="users",
            status=AuditStatus.SUCCESS,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "role": role_name
        }
