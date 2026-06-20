"""
tests/unit/application/test_login_use_case.py — Unit Tests for LoginUseCase
"""

from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.application.use_cases.auth.login_use_case import LoginUseCase
from app.domain.entities.user import User
from app.domain.entities.role import Role
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.role_repository import RoleRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.auth_exceptions import (
    InvalidCredentialsException,
    AccountInactiveException,
)
from app.infrastructure.auth.password_service import PasswordService
from app.core.constants import AuditAction, AuditStatus


@pytest.fixture
def mock_user_repo():
    return MagicMock(spec=UserRepository)


@pytest.fixture
def mock_role_repo():
    return MagicMock(spec=RoleRepository)


@pytest.fixture
def mock_audit_repo():
    repo = MagicMock(spec=AuditLogRepository)
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_login_success(mock_user_repo, mock_role_repo, mock_audit_repo, mock_session):
    # Setup user
    role_id = uuid.uuid4()
    plain_password = "SecurePassword123!"
    hashed_password = PasswordService.hash_password(plain_password)
    
    user = User(
        id=uuid.uuid4(),
        email="teacher@example.com",
        username="teacher1",
        hashed_password=hashed_password,
        full_name="John Doe",
        role_id=role_id,
        is_active=True
    )
    
    role = Role(
        id=role_id,
        name="teacher"
    )

    mock_user_repo.get_by_email = AsyncMock(return_value=user)
    mock_user_repo.update_last_login = AsyncMock()
    mock_role_repo.get_by_id = AsyncMock(return_value=role)

    use_case = LoginUseCase(
        user_repo=mock_user_repo,
        role_repo=mock_role_repo,
        audit_repo=mock_audit_repo,
        session=mock_session
    )

    result = await use_case.execute(
        email="teacher@example.com",
        password=plain_password,
        ip_address="127.0.0.1",
        user_agent="Mozilla/5.0"
    )

    # Assertions
    assert result["username"] == "teacher1"
    assert result["role"] == "teacher"
    assert "access_token" in result
    assert "refresh_token" in result
    assert result["token_type"] == "bearer"

    # Verify repo calls
    mock_user_repo.get_by_email.assert_called_once_with("teacher@example.com")
    mock_user_repo.update_last_login.assert_called_once_with(user.id)
    mock_role_repo.get_by_id.assert_called_once_with(role_id)
    
    # Verify session additions (refresh token model saved)
    assert mock_session.add.call_count == 1
    
    # Verify Audit log saved
    assert mock_audit_repo.save.call_count == 1
    saved_log = mock_audit_repo.save.call_args[0][0]
    assert saved_log.action == AuditAction.LOGIN
    assert saved_log.status == AuditStatus.SUCCESS
    assert saved_log.user_id == user.id


@pytest.mark.asyncio
async def test_login_invalid_email(mock_user_repo, mock_role_repo, mock_audit_repo, mock_session):
    mock_user_repo.get_by_email = AsyncMock(return_value=None)

    use_case = LoginUseCase(
        user_repo=mock_user_repo,
        role_repo=mock_role_repo,
        audit_repo=mock_audit_repo,
        session=mock_session
    )

    with pytest.raises(InvalidCredentialsException):
        await use_case.execute(
            email="nonexistent@example.com",
            password="AnyPassword123!",
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0"
        )

    # Verify failure audit log saved
    assert mock_audit_repo.save.call_count == 1
    saved_log = mock_audit_repo.save.call_args[0][0]
    assert saved_log.action == AuditAction.LOGIN_FAILED
    assert saved_log.status == AuditStatus.FAILURE
    assert saved_log.user_id is None
    assert "Email address not found" in saved_log.error_message


@pytest.mark.asyncio
async def test_login_invalid_password(mock_user_repo, mock_role_repo, mock_audit_repo, mock_session):
    role_id = uuid.uuid4()
    plain_password = "SecurePassword123!"
    hashed_password = PasswordService.hash_password(plain_password)
    
    user = User(
        id=uuid.uuid4(),
        email="teacher@example.com",
        username="teacher1",
        hashed_password=hashed_password,
        full_name="John Doe",
        role_id=role_id,
        is_active=True
    )

    mock_user_repo.get_by_email = AsyncMock(return_value=user)

    use_case = LoginUseCase(
        user_repo=mock_user_repo,
        role_repo=mock_role_repo,
        audit_repo=mock_audit_repo,
        session=mock_session
    )

    with pytest.raises(InvalidCredentialsException):
        await use_case.execute(
            email="teacher@example.com",
            password="WrongPassword123!",
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0"
        )

    # Verify failure audit log saved
    assert mock_audit_repo.save.call_count == 1
    saved_log = mock_audit_repo.save.call_args[0][0]
    assert saved_log.action == AuditAction.LOGIN_FAILED
    assert saved_log.status == AuditStatus.FAILURE
    assert saved_log.user_id == user.id
    assert "Password mismatch" in saved_log.error_message


@pytest.mark.asyncio
async def test_login_account_inactive(mock_user_repo, mock_role_repo, mock_audit_repo, mock_session):
    role_id = uuid.uuid4()
    plain_password = "SecurePassword123!"
    hashed_password = PasswordService.hash_password(plain_password)
    
    user = User(
        id=uuid.uuid4(),
        email="teacher@example.com",
        username="teacher1",
        hashed_password=hashed_password,
        full_name="John Doe",
        role_id=role_id,
        is_active=False  # INACTIVE
    )

    mock_user_repo.get_by_email = AsyncMock(return_value=user)

    use_case = LoginUseCase(
        user_repo=mock_user_repo,
        role_repo=mock_role_repo,
        audit_repo=mock_audit_repo,
        session=mock_session
    )

    with pytest.raises(AccountInactiveException):
        await use_case.execute(
            email="teacher@example.com",
            password=plain_password,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0"
        )

    # Verify failure audit log saved
    assert mock_audit_repo.save.call_count == 1
    saved_log = mock_audit_repo.save.call_args[0][0]
    assert saved_log.action == AuditAction.LOGIN_FAILED
    assert saved_log.status == AuditStatus.FAILURE
    assert saved_log.user_id == user.id
    assert "inactive" in saved_log.error_message
