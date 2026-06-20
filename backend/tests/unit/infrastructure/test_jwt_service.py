"""
tests/unit/infrastructure/test_jwt_service.py — Unit Tests for JWTService
"""

from __future__ import annotations

import uuid
import time
import pytest
import jwt
from app.infrastructure.auth.jwt_service import JWTService
from app.domain.exceptions.auth_exceptions import TokenExpiredException, TokenInvalidException
from app.config import get_settings

settings = get_settings()


def test_create_access_token():
    user_id = uuid.uuid4()
    username = "test_teacher"
    role = "teacher"

    token = JWTService.create_access_token(user_id, username, role)
    assert isinstance(token, str)

    payload = JWTService.verify_token(token, expected_type="access")
    assert payload["sub"] == str(user_id)
    assert payload["username"] == username
    assert payload["role"] == role
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload


def test_create_refresh_token():
    user_id = uuid.uuid4()

    token = JWTService.create_refresh_token(user_id)
    assert isinstance(token, str)

    payload = JWTService.verify_token(token, expected_type="refresh")
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload


def test_verify_token_type_mismatch():
    user_id = uuid.uuid4()
    access_token = JWTService.create_access_token(user_id, "user", "teacher")

    with pytest.raises(TokenInvalidException):
        JWTService.verify_token(access_token, expected_type="refresh")


def test_verify_token_invalid_signature():
    invalid_token = "invalid.token.signature"
    with pytest.raises(TokenInvalidException):
        JWTService.verify_token(invalid_token, expected_type="access")


def test_verify_token_expired(monkeypatch):
    user_id = uuid.uuid4()
    
    # Create an expired token by setting access_token_expire_minutes to negative
    monkeypatch.setattr(settings, "access_token_expire_minutes", -10)
    expired_token = JWTService.create_access_token(user_id, "user", "teacher")
    
    with pytest.raises(TokenExpiredException):
        JWTService.verify_token(expired_token, expected_type="access")


def test_hash_token():
    token = "some_refresh_token_string"
    hashed_1 = JWTService.hash_token(token)
    hashed_2 = JWTService.hash_token(token)

    assert hashed_1 == hashed_2
    assert len(hashed_1) == 64  # SHA-256 is 64 chars in hex
