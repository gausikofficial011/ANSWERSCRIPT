"""
domain/repositories/plagiarism_repository.py — Plagiarism Repository Interface

Defines the abstract interface for PlagiarismReport entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


class PlagiarismRepository(BaseRepository[Any]):
    """
    Abstract repository for PlagiarismReport entities.
    """

    @abstractmethod
    async def get_by_exam_id(self, exam_id: UUID) -> list[Any]:
        """Retrieve all plagiarism reports associated with an exam."""
        ...

    @abstractmethod
    async def get_sheet_similarity_reports(self, answer_sheet_id: UUID) -> list[Any]:
        """Retrieve all reports involving a specific answer sheet (as source or target)."""
        ...

    @abstractmethod
    async def save_batch(self, reports: list[Any]) -> list[Any]:
        """Save a batch of plagiarism reports in a single operation."""
        ...

    @abstractmethod
    async def delete_by_exam_id(self, exam_id: UUID) -> None:
        """Delete all plagiarism reports for an exam (e.g. before recalculating)."""
        ...
