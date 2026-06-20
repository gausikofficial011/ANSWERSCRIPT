"""
domain/repositories/subject_repository.py — Subject Repository Interface

Defines the abstract interface for Subject entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


from app.core.pagination import PaginationParams, PaginatedResponse

class SubjectRepository(BaseRepository[Any]):
    """
    Abstract repository for Subject entities.
    """

    @abstractmethod
    async def get_by_code(self, code: str) -> Any | None:
        """Find a subject by its unique code (case-insensitive)."""
        ...

    @abstractmethod
    async def list_active_subjects(self) -> list[Any]:
        """Retrieve all active subjects."""
        ...

    @abstractmethod
    async def soft_delete(self, subject_id: UUID) -> bool:
        """Soft delete a subject. Returns True if found."""
        ...

    @abstractmethod
    async def list_subjects(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        is_active: bool | None = None
    ) -> PaginatedResponse[Any]:
        """Retrieve paginated subjects matching search and filter parameters."""
        ...

