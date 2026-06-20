"""domain/repositories/answer_sheet_repository.py — Answer Sheet Repository Interface"""

from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from app.core.pagination import PaginatedResponse, PaginationParams
from app.domain.entities.answer_sheet import AnswerSheet
from app.domain.repositories.base_repository import BaseRepository


class AnswerSheetRepository(BaseRepository[AnswerSheet]):
    """
    Abstract repository for AnswerSheet entities.

    Central repository in the system — most processing pipelines
    query and update answer sheets by status.

    Concrete implementation: infrastructure/persistence/repositories/sql_answer_sheet_repository.py
    """

    @abstractmethod
    async def get_by_exam(
        self,
        exam_id: UUID,
        pagination: PaginationParams,
        status: str | None = None,
    ) -> PaginatedResponse[AnswerSheet]:
        """List answer sheets for an exam, optionally filtered by status."""
        ...

    @abstractmethod
    async def get_by_student_and_exam(
        self, student_id: UUID, exam_id: UUID
    ) -> AnswerSheet | None:
        """Find the answer sheet for a specific student in a specific exam."""
        ...

    @abstractmethod
    async def get_by_status(
        self, status: str, limit: int = 50
    ) -> list[AnswerSheet]:
        """Fetch sheets with a specific status (for queue processing)."""
        ...

    @abstractmethod
    async def update_status(
        self,
        answer_sheet_id: UUID,
        status: str,
        error_message: str | None = None,
    ) -> AnswerSheet | None:
        """
        Atomically update only the status field of an answer sheet.
        Used by async Celery workers to report processing state.
        """
        ...

    @abstractmethod
    async def get_by_stored_filename(
        self, stored_filename: str
    ) -> AnswerSheet | None:
        """Find by the UUID-based stored filename (for deduplication)."""
        ...

    @abstractmethod
    async def get_by_hash(self, file_hash: str) -> AnswerSheet | None:
        """Find an answer sheet by its SHA256 file hash."""
        ...

    @abstractmethod
    async def count_by_exam_and_status(
        self, exam_id: UUID, status: str
    ) -> int:
        """Count sheets for analytics and progress reporting."""
        ...

    @abstractmethod
    async def list_answer_sheets(
        self,
        pagination: PaginationParams,
        exam_id: UUID | None = None,
        student_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> PaginatedResponse[AnswerSheet]:
        """Retrieve paginated list of answer sheets matching filters and search."""
        ...

    @abstractmethod
    async def get_all_by_exam_id(self, exam_id: UUID) -> list[AnswerSheet]:
        """Fetch all answer sheets for an exam without pagination."""
        ...
