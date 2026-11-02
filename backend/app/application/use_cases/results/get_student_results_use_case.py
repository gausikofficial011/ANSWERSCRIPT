"""
application/use_cases/results/get_student_results_use_case.py — Get Student Results Use Case
"""

from __future__ import annotations
import uuid
import logging
from sqlalchemy import select

from app.domain.repositories.final_result_repository import FinalResultRepository
from app.domain.repositories.student_repository import StudentRepository
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.subject_repository import SubjectRepository
from app.infrastructure.persistence.models.final_result_model import FinalResultModel

from app.domain.exceptions.domain_exception import EntityNotFoundException

logger = logging.getLogger(__name__)


class GetStudentResultsUseCase:
    """
    Retrieves academic record history for a specific student.
    """

    def __init__(
        self,
        final_result_repo: FinalResultRepository,
        student_repo: StudentRepository,
        exam_repo: ExamRepository,
        subject_repo: SubjectRepository
    ) -> None:
        self.final_result_repo = final_result_repo
        self.student_repo = student_repo
        self.exam_repo = exam_repo
        self.subject_repo = subject_repo

    async def execute(self, student_id: uuid.UUID, only_published: bool = False) -> dict:
        """
        Gathers student profile and academic results history.
        """
        # 1. Fetch Student
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise EntityNotFoundException(entity_type="Student", entity_id=student_id)

        # 2. Fetch all final results for this student
        if hasattr(self.final_result_repo, "session"):
            session = self.final_result_repo.session
            query = select(FinalResultModel).where(FinalResultModel.student_id == student_id)
            result = await session.execute(query)
            models = result.scalars().all()
            results = [self.final_result_repo.to_entity(m) for m in models]
        else:
            # Fallback mock lists
            results = []

        if only_published:
            results = [r for r in results if r.is_published]

        history = []
        for r in results:
            # Fetch Exam info
            exam = await self.exam_repo.get_by_id(r.exam_id)
            if not exam:
                continue

            # Fetch Subject info
            subject = await self.subject_repo.get_by_id(exam.subject_id)
            subject_name = subject.name if subject else "General"

            history.append({
                "exam_id": r.exam_id,
                "exam_title": exam.title,
                "subject_name": subject_name,
                "percentage": r.percentage,
                "grade": r.grade,
                "pass_fail_status": r.pass_fail_status.value if hasattr(r.pass_fail_status, "value") else str(r.pass_fail_status),
                "published_status": "PUBLISHED" if r.is_published else "UNPUBLISHED"
            })

        return {
            "student_id": str(student.id),
            "student_name": student.full_name,
            "student_number": student.student_number,
            "class_section": student.class_section,
            "history": history
        }
