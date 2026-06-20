"""
domain/repositories/user_repository.py — User Repository Interface

Extends BaseRepository[User] with user-specific query methods.
"""

from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from app.domain.entities.user import User
from app.domain.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Abstract repository for User entities.

    Concrete implementation: infrastructure/persistence/repositories/sql_user_repository.py
    """

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Find a user by email address (case-insensitive)."""
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """Find a user by username."""
        ...

    @abstractmethod
    async def get_active_users_by_role(
        self, role: str
    ) -> list[User]:
        """Return all active users with the given role."""
        ...

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Return True if any user (active or not) has this email."""
        ...

    @abstractmethod
    async def username_exists(self, username: str) -> bool:
        """Return True if any user (active or not) has this username."""
        ...

    @abstractmethod
    async def update_last_login(self, user_id: UUID) -> None:
        """Update the last_login_at timestamp for the given user."""
        ...

    @abstractmethod
    async def soft_delete(self, user_id: UUID) -> bool:
        """
        Soft-delete a user by setting deleted_at and is_active=False.
        Returns True if found and soft-deleted.
        """
        ...
