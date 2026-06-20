"""
domain/repositories/extracted_answer_repository.py — ExtractedAnswer Repository Interface

Defines the abstract interface for ExtractedAnswer entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


class ExtractedAnswerRepository(BaseRepository[Any]):
    """
    Abstract repository for ExtractedAnswer entities.
    """

    @abstractmethod
    async def get_by_answer_sheet_id(self, answer_sheet_id: UUID) -> list[Any]:
        """Retrieve all extracted answers for a student's answer sheet."""
        ...

    @abstractmethod
    async def get_by_question_id(self, answer_sheet_id: UUID, question_id: UUID) -> Any | None:
        """Retrieve a specific extracted answer by sheet ID and question ID."""
        ...

    @abstractmethod
    async def save_batch(self, extracted_answers: list[Any]) -> list[Any]:
        """Save a batch of extracted answers in a single operation."""
        ...
