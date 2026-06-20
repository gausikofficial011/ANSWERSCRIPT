"""
domain/repositories/plagiarism_similarity_repository.py — PlagiarismSimilarity Repository Interface
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


class PlagiarismSimilarityRepository(BaseRepository[Any]):
    """
    Abstract repository for PlagiarismSimilarity entities.
    """

    @abstractmethod
    async def list_by_answer_sheet(self, answer_sheet_id: UUID) -> list[Any]:
        """Retrieve similarity pairs where answer_sheet_id is source or target."""
        ...

    @abstractmethod
    async def list_by_question_mapping(self, question_mapping_id: UUID) -> list[Any]:
        """Retrieve similarity pairs where question_mapping_id is source or target."""
        ...

    @abstractmethod
    async def list_by_pair(self, source_answer_sheet_id: UUID, target_answer_sheet_id: UUID) -> list[Any]:
        """Retrieve similarity pairs between two specific answer sheets."""
        ...

    @abstractmethod
    async def delete_by_answer_sheet_id(self, answer_sheet_id: UUID) -> bool:
        """Delete all similarities matching the answer sheet as source or target."""
        ...
