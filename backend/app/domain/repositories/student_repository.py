"""
domain/repositories/student_repository.py — Student Repository Interface

Defines the abstract interface for Student entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


from app.core.pagination import PaginationParams, PaginatedResponse

class StudentRepository(BaseRepository[Any]):
    """
    Abstract repository for Student entities.
    """

    @abstractmethod
    async def get_by_student_number(self, student_number: str) -> Any | None:
        """Find a student by their unique student number."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Any | None:
        """Find a student by their email address."""
        ...

    @abstractmethod
    async def soft_delete(self, student_id: UUID) -> bool:
        """Soft delete a student by setting deleted_at. Returns True if found."""
        ...

    @abstractmethod
    async def list_students(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        class_section: str | None = None
    ) -> PaginatedResponse[Any]:
        """Retrieve paginated students matching search and section filters."""
        ...

