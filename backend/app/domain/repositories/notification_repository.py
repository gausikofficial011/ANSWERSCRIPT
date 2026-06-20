"""
domain/repositories/notification_repository.py — Notification Repository Interface

Defines the abstract interface for Notification entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Any]):
    """
    Abstract repository for Notification entities.
    """

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, is_read: bool | None = None) -> list[Any]:
        """Retrieve notifications for a user, optionally filtered by read status."""
        ...

    @abstractmethod
    async def get_unread_count(self, user_id: UUID) -> int:
        """Count unread notifications for a user."""
        ...

    @abstractmethod
    async def mark_as_read(self, notification_id: UUID) -> bool:
        """Mark a notification as read. Returns True if successful."""
        ...

    @abstractmethod
    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user. Returns the count updated."""
        ...
