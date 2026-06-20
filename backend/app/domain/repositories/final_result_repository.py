"""
domain/repositories/final_result_repository.py — FinalResult Repository Interface

Defines the abstract interface for FinalResult entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository


class FinalResultRepository(BaseRepository[Any]):
    """
    Abstract repository for FinalResult entities.
    """

    @abstractmethod
    async def get_by_answer_sheet_id(self, answer_sheet_id: UUID) -> Any | None:
        """Retrieve the final result for a student's answer sheet."""
        ...

    @abstractmethod
    async def get_by_exam_id(self, exam_id: UUID) -> list[Any]:
        """Retrieve all student final results for an exam."""
        ...

    @abstractmethod
    async def get_student_exam_result(self, student_id: UUID, exam_id: UUID) -> Any | None:
        """Retrieve a specific student's result for a specific exam."""
        ...

    @abstractmethod
    async def publish_exam_results(self, exam_id: UUID, publisher_id: UUID) -> int:
        """Publish all results for an exam. Returns the number of results published."""
        ...
