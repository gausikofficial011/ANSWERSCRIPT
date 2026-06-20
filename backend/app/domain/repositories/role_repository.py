"""
domain/repositories/role_repository.py — Role Repository Interface

Defines the abstract interface for Role entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Any]):
    """
    Abstract repository for Role entities.
    """

    @abstractmethod
    async def get_by_name(self, name: str) -> Any | None:
        """Find a role by its name (e.g. 'admin', 'teacher')."""
        ...
