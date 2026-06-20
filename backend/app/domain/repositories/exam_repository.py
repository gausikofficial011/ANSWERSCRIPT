"""
domain/repositories/exam_repository.py — Exam Repository Interface

Defines the abstract interface for Exam entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


from app.core.pagination import PaginationParams, PaginatedResponse

class ExamRepository(BaseRepository[Any]):
    """
    Abstract repository for Exam entities.
    """

    @abstractmethod
    async def get_by_subject_id(self, subject_id: UUID) -> list[Any]:
        """Retrieve all exams associated with a subject."""
        ...

    @abstractmethod
    async def get_by_status(self, status: str) -> list[Any]:
        """Retrieve all exams filtered by status."""
        ...

    @abstractmethod
    async def soft_delete(self, exam_id: UUID) -> bool:
        """Soft delete an exam. Returns True if found."""
        ...

    @abstractmethod
    async def list_exams(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        subject_id: UUID | None = None,
        status: str | None = None
    ) -> PaginatedResponse[Any]:
        """Retrieve paginated exams matching filters and search."""
        ...

