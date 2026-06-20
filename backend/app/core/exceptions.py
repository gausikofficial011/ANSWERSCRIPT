"""
core/exceptions.py — HTTP Exception Factory

Maps domain-layer exceptions to FastAPI HTTPException responses.
This is the boundary between the domain's exception vocabulary
and the HTTP presentation layer.

Design:
  - Domain layer raises DomainException subclasses (no HTTP knowledge).
  - This module converts them to appropriate HTTP status codes.
  - API routers import these factories; they never import domain exceptions directly.
"""

from fastapi import HTTPException, status


# ── 400 Bad Request ───────────────────────────────────────────────────────────

def bad_request(detail: str) -> HTTPException:
    """Malformed input or business rule violation."""
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


# ── 401 Unauthorized ──────────────────────────────────────────────────────────

def unauthorized(detail: str = "Authentication required.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def invalid_credentials() -> HTTPException:
    return unauthorized("Invalid email or password.")


def token_expired() -> HTTPException:
    return unauthorized("Access token has expired.")


def token_invalid() -> HTTPException:
    return unauthorized("Access token is invalid.")


# ── 403 Forbidden ─────────────────────────────────────────────────────────────

def forbidden(detail: str = "You do not have permission to perform this action.") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def insufficient_role(required_role: str) -> HTTPException:
    return forbidden(f"This action requires the '{required_role}' role.")


# ── 404 Not Found ─────────────────────────────────────────────────────────────

def not_found(resource: str, resource_id: str | None = None) -> HTTPException:
    detail = f"{resource} not found."
    if resource_id:
        detail = f"{resource} with id '{resource_id}' not found."
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


# ── 409 Conflict ──────────────────────────────────────────────────────────────

def conflict(detail: str) -> HTTPException:
    """Resource already exists or state conflict."""
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def duplicate_resource(resource: str, field: str, value: str) -> HTTPException:
    return conflict(f"{resource} with {field} '{value}' already exists.")


# ── 413 Payload Too Large ─────────────────────────────────────────────────────

def file_too_large(max_mb: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail=f"File exceeds the maximum allowed size of {max_mb} MB.",
    )


# ── 415 Unsupported Media Type ────────────────────────────────────────────────

def unsupported_file_type(allowed: list[str]) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail=f"Unsupported file type. Allowed types: {', '.join(allowed)}.",
    )


# ── 422 Unprocessable Entity ─────────────────────────────────────────────────

def unprocessable(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
    )


# ── 429 Too Many Requests ────────────────────────────────────────────────────

def rate_limited() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many requests. Please slow down.",
    )


# ── 500 Internal Server Error ─────────────────────────────────────────────────

def internal_error(detail: str = "An unexpected error occurred.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
    )


def ocr_processing_error() -> HTTPException:
    return internal_error("OCR processing failed. Please retry or contact support.")


def evaluation_error() -> HTTPException:
    return internal_error("AI evaluation failed. Please retry or contact support.")


# ── 503 Service Unavailable ───────────────────────────────────────────────────

def service_unavailable(service: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"{service} is temporarily unavailable.",
    )
