"""
domain/repositories/question_mapping_repository.py — QuestionMapping Repository Interface
"""

from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from app.domain.entities.question_mapping import QuestionMapping
from app.domain.repositories.base_repository import BaseRepository


class QuestionMappingRepository(BaseRepository[QuestionMapping]):
    """
    Abstract repository for QuestionMapping entities.
    """

    @abstractmethod
    async def list_by_answer_sheet_id(self, answer_sheet_id: UUID) -> list[QuestionMapping]:
        """Retrieve all question mapping records associated with an answer sheet."""
        ...

    @abstractmethod
    async def delete_by_answer_sheet_id(self, answer_sheet_id: UUID) -> bool:
        """Delete all question mapping records associated with an answer sheet."""
        ...
