"""
api/v1/routers/auth.py — Authentication Endpoints

Exposes REST APIs for logging in, logging out, rotating refresh tokens, changing passwords,
and retrieving the currently logged-in user profile.
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth
from app.api.v1.schemas.auth_schemas import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordChangeRequest,
    CurrentUserResponse,
)
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository
from app.infrastructure.persistence.repositories.sql_role_repository import SqlRoleRepository
from app.infrastructure.persistence.repositories.sql_audit_log_repository import SqlAuditLogRepository
from app.application.use_cases.auth import (
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
    ChangePasswordUseCase,
)
from app.domain.entities.user import User
from app.domain.exceptions.auth_exceptions import (
    InvalidCredentialsException,
    AccountInactiveException,
    TokenInvalidException,
    TokenRevokedException,
)
from app.core.exceptions import (
    invalid_credentials,
    unauthorized,
    bad_request,
)
from app.infrastructure.auth.jwt_service import JWTService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user by email and password, generate access and refresh tokens, and log audit event."
)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    user_repo = SqlUserRepository(db)
    role_repo = SqlRoleRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    
    use_case = LoginUseCase(user_repo, role_repo, audit_repo, session=db)
    
    # Extract client IP & User-Agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    try:
        result = await use_case.execute(
            email=payload.email,
            password=payload.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return TokenResponse(**result)
    except InvalidCredentialsException:
        raise invalid_credentials()
    except AccountInactiveException as e:
        raise unauthorized(str(e))


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Revoke the provided refresh token and record logout audit event."
)
async def logout(
    payload: RefreshTokenRequest,
    request: Request,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
):
    audit_repo = SqlAuditLogRepository(db)
    use_case = LogoutUseCase(audit_repo, session=db)
    
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    await use_case.execute(
        refresh_token=payload.refresh_token,
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    return {"detail": "Successfully logged out."}


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Token Refresh",
    description="Rotates the refresh token (RTR) and issues a new access/refresh token pair."
)
async def refresh(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    user_repo = SqlUserRepository(db)
    role_repo = SqlRoleRepository(db)
    use_case = RefreshTokenUseCase(user_repo, role_repo, session=db)
    
    try:
        # Perform token verification first to extract user id in case rotation succeeds
        token_payload = JWTService.verify_token(payload.refresh_token, expected_type="refresh")
        user_id = uuid.UUID(token_payload["sub"])
        
        result = await use_case.execute(refresh_token=payload.refresh_token)
        
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise unauthorized("User not found.")
            
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            user_id=user.id,
            username=user.username,
            role=user.role or "teacher"
        )
    except (TokenInvalidException, TokenRevokedException):
        raise unauthorized("The provided refresh token is invalid or has expired.")
    except AccountInactiveException as e:
        raise unauthorized(str(e))


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change Password",
    description="Verify current password and set a new password, revoking other active sessions."
)
async def change_password(
    payload: PasswordChangeRequest,
    request: Request,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
):
    user_repo = SqlUserRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = ChangePasswordUseCase(user_repo, audit_repo, session=db)
    
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    try:
        await use_case.execute(
            user_id=current_user.id,
            old_password=payload.old_password,
            new_password=payload.new_password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return {"detail": "Password changed successfully."}
    except InvalidCredentialsException:
        raise invalid_credentials()
    except ValueError as e:
        raise bad_request(str(e))


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Retrieve details of the currently authenticated user session."
)
async def get_me(
    current_user: User = Depends(require_auth)
) -> CurrentUserResponse:
    return current_user
