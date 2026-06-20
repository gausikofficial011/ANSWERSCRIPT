"""
api/v1/dependencies/auth.py — Authentication & Authorization Dependencies

FastAPI Depends() callables for extracting and validating the current user
from incoming JWT tokens. Used by protected routers.

Usage in routers:
    from app.api.v1.dependencies.auth import require_auth, require_admin, require_teacher

    @router.get("/exams")
    async def list_exams(current_user: User = Depends(require_auth)):
        ...

    @router.delete("/users/{id}")
    async def delete_user(
        user_id: UUID,
        current_user: User = Depends(require_admin),  # Admin only
    ):
        ...
"""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.constants import UserRole
from app.domain.entities.user import User
from app.infrastructure.persistence.database import get_db_session

# Bearer token extractor — raises 403 if Authorization header is missing
_bearer_scheme = HTTPBearer(auto_error=True)



async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db = Depends(get_db_session)
) -> User:
    """
    Extract and validate the JWT Bearer token from the Authorization header.

    Returns the authenticated User domain entity.
    Raises 401 if token is missing, expired, or invalid.
    """
    import uuid
    from app.infrastructure.auth.jwt_service import JWTService
    from app.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository
    from app.domain.exceptions.auth_exceptions import TokenExpiredException, TokenInvalidException
    from app.core.exceptions import token_expired, token_invalid, unauthorized

    token = credentials.credentials
    try:
        payload = JWTService.verify_token(token, expected_type="access")
    except TokenExpiredException:
        raise token_expired()
    except TokenInvalidException:
        raise token_invalid()

    user_id_str = payload.get("sub")
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        raise token_invalid()

    user_repo = SqlUserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise unauthorized("User not found.")

    if not user.is_active:
        raise unauthorized("User account is deactivated.")

    # Fallback to token payload role if not populated
    if user.role is None:
        user.role = payload.get("role")

    return user



async def require_auth(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency: User must be authenticated (any role).

    Returns:
        Authenticated User entity.
    """
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency: User must have the Admin role.

    Raises:
        403 Forbidden if user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        from app.core.exceptions import insufficient_role
        raise insufficient_role("admin")
    return current_user


async def require_teacher(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency: User must have the Teacher role (or Admin).
    Admins can perform all teacher actions.

    Raises:
        403 Forbidden if user has neither admin nor teacher role.
    """
    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER):
        from app.core.exceptions import insufficient_role
        raise insufficient_role("teacher")
    return current_user
