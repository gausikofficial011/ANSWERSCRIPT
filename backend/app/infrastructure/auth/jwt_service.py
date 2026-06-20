"""
infrastructure/auth/jwt_service.py — JWT Token Service

Handles the encoding, decoding, validation, and metadata extraction
for JWT access and refresh tokens.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
import jwt

from app.config import get_settings
from app.domain.exceptions.auth_exceptions import TokenExpiredException, TokenInvalidException

settings = get_settings()


class JWTService:
    """
    Utility service for JWT creation and validation.
    """

    @staticmethod
    def create_access_token(user_id: uuid.UUID, username: str, role: str) -> str:
        """
        Generate a short-lived JWT access token.
        """
        now = datetime.now(timezone.utc)
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
        expire = now + expires_delta

        payload = {
            "sub": str(user_id),
            "username": username,
            "role": role,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": str(uuid.uuid4())
        }

        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return token

    @staticmethod
    def create_refresh_token(user_id: uuid.UUID) -> str:
        """
        Generate a long-lived session refresh token.
        """
        now = datetime.now(timezone.utc)
        expires_delta = timedelta(days=settings.refresh_token_expire_days)
        expire = now + expires_delta

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": str(uuid.uuid4())
        }

        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return token

    @staticmethod
    def verify_token(token: str, expected_type: str = "access") -> dict:
        """
        Verify a JWT token's signature, expiry, and structure.

        Args:
            token: The raw JWT string.
            expected_type: Either 'access' or 'refresh' to prevent token swapping.

        Returns:
            The parsed token payload dictionary.

        Raises:
            TokenExpiredException: If exp claim is in the past.
            TokenInvalidException: If decoding fails or type mismatch occurs.
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                options={"require": ["sub", "exp", "type", "jti"]}
            )

            if payload.get("type") != expected_type:
                raise TokenInvalidException()

            return payload

        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except (jwt.InvalidTokenError, jwt.PyJWTError):
            raise TokenInvalidException()

    @staticmethod
    def hash_token(token: str) -> str:
        """
        Generate a SHA-256 hash of a token string for safe DB storage.
        We do not store plaintext refresh tokens in the database.
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
