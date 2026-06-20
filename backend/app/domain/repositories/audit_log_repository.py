"""
domain/repositories/audit_log_repository.py — AuditLog Repository Interface

Defines the abstract interface for AuditLog entity data operations.
"""

from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.repositories.base_repository import BaseRepository
from app.core.pagination import PaginatedResponse, PaginationParams


class AuditLogRepository(BaseRepository[Any]):
    """
    Abstract repository for AuditLog entities.
    """

    @abstractmethod
    async def filter_logs(
        self,
        user_id: UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: UUID | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        pagination: PaginationParams = PaginationParams(),
    ) -> PaginatedResponse[Any]:
        """Query and filter audit logs with pagination."""
        ...
