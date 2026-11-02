"""
infrastructure/security/rate_limiter.py — In-Memory Rate Limiter Service
"""

from __future__ import annotations

import time
import logging
from threading import Lock
from fastapi import Request, HTTPException, Depends, status

from app.config import get_settings
from app.domain.entities.user import User
from app.api.v1.dependencies.auth import require_auth

logger = logging.getLogger(__name__)


class InMemoryRateLimiter:
    """
    Lightweight, thread-safe in-memory rate limiter using sliding windows.
    Does not require Redis or external infrastructure.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._history: dict[str, list[float]] = {}

    def is_rate_limited(self, key: str, limit: int, window_seconds: int) -> bool:
        """
        Check if a request key has exceeded limit requests within the window.
        Returns True if limited, False otherwise.
        """
        now = time.time()
        cutoff = now - window_seconds

        with self._lock:
            # 1. Retrieve history and purge expired timestamps
            timestamps = self._history.get(key, [])
            timestamps = [t for t in timestamps if t > cutoff]

            # 2. Check if limit is exceeded
            if len(timestamps) >= limit:
                self._history[key] = timestamps
                return True

            # 3. Append current timestamp and save
            timestamps.append(now)
            self._history[key] = timestamps

            # 4. Periodically cleanup database to avoid memory leaks
            if len(self._history) > 1000:
                self._cleanup_old_records(now - (window_seconds * 2))

            return False

    def _cleanup_old_records(self, cutoff: float) -> None:
        """Helper to purge stale entries from history dict."""
        keys_to_delete = []
        for key, timestamps in self._history.items():
            cleaned = [t for t in timestamps if t > cutoff]
            if not cleaned:
                keys_to_delete.append(key)
            else:
                self._history[key] = cleaned
        for key in keys_to_delete:
            del self._history[key]


# Global rate limiter instance
upload_rate_limiter = InMemoryRateLimiter()


async def upload_rate_limit_dependency(
    request: Request,
    current_user: User = Depends(require_auth)
) -> None:
    """
    FastAPI dependency for enforcing rate limits on answer sheet uploads.
    Enforces per-IP and per-User constraints.
    """
    settings = get_settings()
    ip_address = request.client.host if request.client else "unknown"

    limit = settings.rate_limit_upload_limit
    window = settings.rate_limit_upload_window

    # 1. IP check
    ip_key = f"upload_ip:{ip_address}"
    if upload_rate_limiter.is_rate_limited(ip_key, limit, window):
        logger.warning(f"Upload rate limit exceeded for IP: {ip_address}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many upload requests from this IP. Please try again later."
        )

    # 2. User check
    user_key = f"upload_user:{current_user.id}"
    if upload_rate_limiter.is_rate_limited(user_key, limit, window):
        logger.warning(f"Upload rate limit exceeded for User: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many upload requests from this user. Please try again later."
        )
