"""
application/use_cases/auth/refresh_token_use_case.py — Refresh Token Use Case

Implements Refresh Token Rotation (RTR). Validates the incoming refresh token,
revokes it, detects reuse, and issues a new access/refresh token pair.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update

from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.role_repository import RoleRepository
from app.domain.exceptions.auth_exceptions import (
    TokenRevokedException,
    TokenInvalidException,
    AccountInactiveException
)
from app.infrastructure.auth.jwt_service import JWTService
from app.config import get_settings

settings = get_settings()


class RefreshTokenUseCase:
    """
    Orchestrates validation of refresh tokens and rotates them.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        session: any
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.session = session

    async def execute(
        self,
        refresh_token: str
    ) -> dict[str, str]:
        # 1. Decode token
        payload = JWTService.verify_token(refresh_token, expected_type="refresh")
        user_id = uuid.UUID(payload["sub"])

        # 2. Check if user is active
        user = await self.user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AccountInactiveException()

        # 3. Hash the token for DB lookup
        token_hash = JWTService.hash_token(refresh_token)

        # 4. Lookup token in DB
        from app.infrastructure.persistence.models.refresh_token_model import RefreshTokenModel
        
        query = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        result = await self.session.execute(query)
        db_token = result.scalar_one_or_none()

        if db_token is None:
            raise TokenInvalidException()

        # Check for reuse / theft (RTR protection mechanism)
        if db_token.is_revoked:
            # Token was already used! Revoke all tokens for this user as a precaution
            stmt = (
                update(RefreshTokenModel)
                .where(RefreshTokenModel.user_id == user_id)
                .values(is_revoked=True, updated_at=datetime.now(timezone.utc))
            )
            await self.session.execute(stmt)
            raise TokenRevokedException()

        # Check expiration
        now_utc = datetime.now(timezone.utc)
        # Ensure db_token.expires_at is timezone-aware
        expires_at = db_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now_utc:
            raise TokenRevokedException()

        # 5. Perform Rotation (RTR)
        # Mark old token as revoked/used
        db_token.is_revoked = True
        db_token.updated_at = now_utc

        # Generate new tokens
        role = await self.role_repo.get_by_id(user.role_id)
        role_name = role.name if role else "teacher"

        new_access_token = JWTService.create_access_token(user.id, user.username, role_name)
        new_refresh_token = JWTService.create_refresh_token(user.id)

        # Save new refresh token in DB
        new_hashed_rt = JWTService.hash_token(new_refresh_token)
        new_expires_at = now_utc + timedelta(days=settings.refresh_token_expire_days)

        new_db_token = RefreshTokenModel(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=new_hashed_rt,
            expires_at=new_expires_at,
            is_revoked=False,
            created_at=now_utc,
            updated_at=now_utc
        )
        self.session.add(new_db_token)
        await self.session.flush()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
