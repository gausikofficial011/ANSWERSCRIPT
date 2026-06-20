"""
domain/repositories/question_repository.py — Question Repository Interface

Defines the abstract interface for Question entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


from app.core.pagination import PaginationParams, PaginatedResponse

class QuestionRepository(BaseRepository[Any]):
    """
    Abstract repository for Question entities.
    """

    @abstractmethod
    async def get_by_exam_id(self, exam_id: UUID) -> list[Any]:
        """Retrieve all questions for a given exam, ordered by question number."""
        ...

    @abstractmethod
    async def get_by_number(self, exam_id: UUID, question_number: int) -> Any | None:
        """Retrieve a specific question by exam ID and question number."""
        ...

    @abstractmethod
    async def list_questions(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        exam_id: UUID | None = None
    ) -> PaginatedResponse[Any]:
        """Retrieve paginated questions matching exam filter and search query."""
        ...

