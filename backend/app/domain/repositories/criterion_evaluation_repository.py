"""
domain/repositories/criterion_evaluation_repository.py — CriterionEvaluation Repository Interface

Defines the abstract interface for CriterionEvaluation entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


class CriterionEvaluationRepository(BaseRepository[Any]):
    """
    Abstract repository for CriterionEvaluation entities.
    """

    @abstractmethod
    async def get_by_evaluation_id(self, evaluation_id: UUID) -> list[Any]:
        """Retrieve all criterion evaluations for a question evaluation, ordered by criterion."""
        ...

    @abstractmethod
    async def get_by_criterion_id(self, evaluation_id: UUID, criterion_id: UUID) -> Any | None:
        """Retrieve the evaluation for a specific rubric criterion."""
        ...

    @abstractmethod
    async def save_batch(self, criterion_evaluations: list[Any]) -> list[Any]:
        """Save a batch of criterion evaluations in a single operation."""
        ...
