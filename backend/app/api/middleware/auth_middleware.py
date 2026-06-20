"""
api/middleware/auth_middleware.py — Authentication Middleware

Extracts JWT tokens from headers and stores the parsed claims in the Request state.
This avoids repetitive JWT parsing in logging, rate limiting, and other middlewares,
while leaving database lookups and strict security enforcement to route dependencies.
"""

from __future__ import annotations

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.infrastructure.auth.jwt_service import JWTService
from app.domain.exceptions.auth_exceptions import TokenExpiredException, TokenInvalidException


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to decode JWT access token claims and attach them to Request state.
    
    Attaches:
      - request.state.user_id (str | None)
      - request.state.username (str | None)
      - request.state.role (str | None)
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Initialize default request state
        request.state.user_id = None
        request.state.username = None
        request.state.role = None

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()  # Strip "Bearer " prefix
            if token:
                try:
                    payload = JWTService.verify_token(token, expected_type="access")
                    request.state.user_id = payload.get("sub")
                    request.state.username = payload.get("username")
                    request.state.role = payload.get("role")
                except (TokenExpiredException, TokenInvalidException):
                    # Do not block request here; let the router dependencies (Depends(require_auth))
                    # handle authorization failures. This keeps public endpoints accessible.
                    pass

        return await call_next(request)
