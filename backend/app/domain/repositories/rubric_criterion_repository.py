"""
domain/repositories/rubric_criterion_repository.py — RubricCriterion Repository Interface

Defines the abstract interface for RubricCriterion entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


class RubricCriterionRepository(BaseRepository[Any]):
    """
    Abstract repository for RubricCriterion entities.
    """

    @abstractmethod
    async def get_by_rubric_id(self, rubric_id: UUID) -> list[Any]:
        """Retrieve all criteria for a rubric, ordered by order_index."""
        ...

    @abstractmethod
    async def save_batch(self, criteria: list[Any]) -> list[Any]:
        """Save a batch of rubric criteria in a single operation."""
        ...
