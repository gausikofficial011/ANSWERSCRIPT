"""
domain/repositories/evaluation_revision_repository.py — EvaluationRevision Repository Interface

Defines the abstract interface for EvaluationRevision entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


class EvaluationRevisionRepository(BaseRepository[Any]):
    """
    Abstract repository for EvaluationRevision entities.
    """

    @abstractmethod
    async def get_by_evaluation_id(self, evaluation_id: UUID) -> list[Any]:
        """Retrieve all historical score revisions for an evaluation, ordered by revision number."""
        ...

    @abstractmethod
    async def get_next_revision_number(self, evaluation_id: UUID) -> int:
        """Get the next sequential revision number for an evaluation."""
        ...
