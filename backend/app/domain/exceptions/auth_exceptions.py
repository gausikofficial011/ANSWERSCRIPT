"""domain/exceptions/auth_exceptions.py — Authentication & Authorization Exceptions"""

from app.domain.exceptions.domain_exception import DomainException


class AuthenticationException(DomainException):
    """Base for all authentication-related failures."""


class InvalidCredentialsException(AuthenticationException):
    """Raised when email/password combination does not match any user."""

    def __init__(self) -> None:
        super().__init__("Invalid email or password.")


class AccountInactiveException(AuthenticationException):
    """Raised when the user account exists but has been deactivated."""

    def __init__(self) -> None:
        super().__init__(
            "Your account has been deactivated. Please contact an administrator."
        )


class TokenExpiredException(AuthenticationException):
    """Raised when a JWT access or refresh token has expired."""

    def __init__(self) -> None:
        super().__init__("The provided token has expired.")


class TokenInvalidException(AuthenticationException):
    """Raised when a JWT token cannot be decoded or has been tampered with."""

    def __init__(self) -> None:
        super().__init__("The provided token is invalid.")


class TokenRevokedException(AuthenticationException):
    """Raised when a refresh token has been explicitly revoked (logout)."""

    def __init__(self) -> None:
        super().__init__("The provided token has been revoked.")


class AuthorizationException(DomainException):
    """
    Raised when an authenticated user attempts an action they lack
    permission to perform.
    """

    def __init__(self, action: str | None = None) -> None:
        msg = "You are not authorized to perform this action."
        if action:
            msg = f"You are not authorized to: {action}."
        super().__init__(msg)
