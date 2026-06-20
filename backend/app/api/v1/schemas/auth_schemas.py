"""
api/v1/schemas/auth_schemas.py — Authentication Request/Response Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    """Request payload for logging in."""
    email: str = Field(..., description="User's registered email address.")
    password: str = Field(..., description="User's password.")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        from app.domain.value_objects.email import Email
        try:
            email_vo = Email(v)
            return str(email_vo)
        except ValueError as e:
            raise ValueError(str(e))


class TokenResponse(BaseModel):
    """Response payload containing JWT tokens after successful authentication/refresh."""
    access_token: str = Field(..., description="JWT access token.")
    refresh_token: str = Field(..., description="JWT refresh token.")
    token_type: str = Field("bearer", description="Token authentication scheme (always Bearer).")
    user_id: uuid.UUID = Field(..., description="ID of the authenticated user.")
    username: str = Field(..., description="Username of the authenticated user.")
    role: str = Field(..., description="Role assigned to the user (e.g. admin, teacher).")


class RefreshTokenRequest(BaseModel):
    """Request payload for rotating/refreshing access tokens."""
    refresh_token: str = Field(..., description="The refresh token issued to the user.")


class PasswordChangeRequest(BaseModel):
    """Request payload for changing password."""
    old_password: str = Field(..., description="Current plaintext password.")
    new_password: str = Field(..., description="New plaintext password to set.")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        from app.domain.value_objects.password import Password
        try:
            Password(v)
            return v
        except ValueError as e:
            raise ValueError(str(e))


class CurrentUserResponse(BaseModel):
    """Response payload showing detail of the currently logged-in user context."""
    id: uuid.UUID = Field(..., description="Unique user identifier.")
    email: str = Field(..., description="User's email address.")
    username: str = Field(..., description="User's unique username.")
    full_name: str = Field(..., description="User's full display name.")
    role: str = Field(..., description="Assigned role name (e.g., admin, teacher).")
    is_active: bool = Field(..., description="Indicates if user's account is active.")
    is_verified: bool = Field(..., description="Indicates if user's email is verified.")
    last_login_at: datetime | None = Field(None, description="Timestamp of user's last successful login.")
    created_at: datetime = Field(..., description="Timestamp of account creation.")

    class Config:
        from_attributes = True
