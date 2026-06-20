"""
domain/repositories/rubric_repository.py — Rubric Repository Interface

Defines the abstract interface for Rubric entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


from app.core.pagination import PaginationParams, PaginatedResponse

class RubricRepository(BaseRepository[Any]):
    """
    Abstract repository for Rubric entities (Aggregate Root).
    """

    @abstractmethod
    async def get_active_by_question_id(self, question_id: UUID) -> Any | None:
        """Retrieve the active rubric version for a question."""
        ...

    @abstractmethod
    async def list_versions_by_question_id(self, question_id: UUID) -> list[Any]:
        """Retrieve all versions of rubrics for a question, ordered by version DESC."""
        ...

    @abstractmethod
    async def deactivate_all_for_question(self, question_id: UUID) -> None:
        """Deactivate all rubrics for a question (before activating a new one)."""
        ...

    @abstractmethod
    async def list_rubrics(
        self,
        pagination: PaginationParams,
        question_id: UUID | None = None,
        is_active: bool | None = None
    ) -> PaginatedResponse[Any]:
        """Retrieve paginated rubrics matching search and filters."""
        ...

