"""
infrastructure/storage/default_student_mapping_service.py — Default Student Mapping Service
"""

from __future__ import annotations

import re
import uuid
from app.domain.services.student_mapping_service import StudentMappingService
from app.domain.repositories.student_repository import StudentRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException


class DefaultStudentMappingService(StudentMappingService):
    """
    Concrete service matching files to registered student records.
    """

    def __init__(self, student_repo: StudentRepository):
        self.student_repo = student_repo

    async def map_student(
        self,
        filename: str,
        file_data: bytes,
        manual_student_id: uuid.UUID | None = None
    ) -> uuid.UUID:
        # Priority 1: Manual student_id selection
        if manual_student_id is not None:
            student = await self.student_repo.get_by_id(manual_student_id)
            if not student:
                raise EntityNotFoundException(entity_type="Student", entity_id=manual_student_id)
            return student.id

        # Priority 2: Filename extraction matching student registration/student number
        filename_cleaned = Path(filename).stem
        
        # Check direct match of clean filename to student number
        student = await self.student_repo.get_by_student_number(filename_cleaned.strip())
        if student:
            return student.id

        # Tokenize by common delimiters and search each token
        tokens = re.split(r'[_\-\s]+', filename_cleaned)
        for token in tokens:
            token_clean = token.strip()
            if len(token_clean) >= 2:  # Ignore tiny tokens
                student = await self.student_repo.get_by_student_number(token_clean)
                if student:
                    return student.id

        # Priority 3: OCR fallback (stub hook for future Phase 6 integration)
        ocr_student_id = await self._ocr_mapping_fallback(filename, file_data)
        if ocr_student_id is not None:
            return ocr_student_id

        raise BusinessRuleViolationException(
            rule=f"Could not map filename '{filename}' to any student. "
                 f"Please rename the file to include the student's registration number."
        )

    async def _ocr_mapping_fallback(self, filename: str, file_data: bytes) -> uuid.UUID | None:
        """
        Placeholder stub for Phase 6 OCR-based student identification.
        """
        return None


# Helper to allow Path usage inside the service
from pathlib import Path
