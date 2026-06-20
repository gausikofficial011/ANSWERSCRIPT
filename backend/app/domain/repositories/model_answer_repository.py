"""
domain/repositories/model_answer_repository.py — ModelAnswer Repository Interface

Defines the abstract interface for ModelAnswer entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


from app.core.pagination import PaginationParams, PaginatedResponse

class ModelAnswerRepository(BaseRepository[Any]):
    """
    Abstract repository for ModelAnswer entities.
    """

    @abstractmethod
    async def get_by_question_id(self, question_id: UUID) -> Any | None:
        """Retrieve the model answer associated with a question."""
        ...

    @abstractmethod
    async def list_model_answers(
        self,
        pagination: PaginationParams,
        question_id: UUID | None = None
    ) -> PaginatedResponse[Any]:
        """Retrieve paginated model answers, optionally filtering by question ID."""
        ...

