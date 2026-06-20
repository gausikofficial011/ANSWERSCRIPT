"""
domain/repositories/evaluation_repository.py — Evaluation Repository Interface

Defines the abstract interface for Evaluation entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


class EvaluationRepository(BaseRepository[Any]):
    """
    Abstract repository for Evaluation entities.
    """

    @abstractmethod
    async def get_by_answer_sheet_id(self, answer_sheet_id: UUID) -> list[Any]:
        """Retrieve all evaluations associated with an answer sheet."""
        ...

    @abstractmethod
    async def get_by_question_id(self, answer_sheet_id: UUID, question_id: UUID) -> Any | None:
        """Retrieve the evaluation for a specific question on an answer sheet."""
        ...

    @abstractmethod
    async def save_batch(self, evaluations: list[Any]) -> list[Any]:
        """Save a batch of evaluations in a single operation."""
        ...

    @abstractmethod
    async def get_pending_verifications(self, exam_id: UUID | None = None) -> list[Any]:
        """Retrieve evaluations awaiting teacher verification, optionally filtered by exam."""
        ...
