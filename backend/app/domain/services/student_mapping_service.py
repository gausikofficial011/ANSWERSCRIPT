"""
domain/services/student_mapping_service.py — Abstract Student Mapping Service
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod


class StudentMappingService(ABC):
    """
    Abstract contract for mapping an uploaded answer sheet's identity properties
    (like original filename or metadata) to a Student domain entity ID.
    """

    @abstractmethod
    async def map_student(
        self,
        filename: str,
        file_data: bytes,
        manual_student_id: uuid.UUID | None = None
    ) -> uuid.UUID:
        """
        Attempts to resolve the Student entity ID for a file.

        Priority:
        1. Manual student_id selection.
        2. Filename extraction matching student registration/student number.
        3. Future OCR-based extraction mapping (plugged in later).

        Raises:
            BusinessRuleViolationException if the student cannot be mapped.
        """
        ...
