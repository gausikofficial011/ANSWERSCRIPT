"""
application/use_cases/results/get_exam_results_use_case.py — Get Exam Results Use Case
"""

from __future__ import annotations
import math
import uuid
import logging

from app.domain.repositories.final_result_repository import FinalResultRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.student_repository import StudentRepository
from app.application.services.final_result_synchronization_service import FinalResultSynchronizationService

from app.core.constants import AnswerSheetStatus
from app.domain.exceptions.domain_exception import EntityNotFoundException

logger = logging.getLogger(__name__)


class GetExamResultsUseCase:
    """
    Retrieves, searches, and paginates final scores list for an exam.
    Triggers automatic on-demand synchronization for verified papers without result records.
    """

    def __init__(
        self,
        final_result_repo: FinalResultRepository,
        answer_sheet_repo: AnswerSheetRepository,
        exam_repo: ExamRepository,
        student_repo: StudentRepository,
        sync_service: FinalResultSynchronizationService
    ) -> None:
        self.final_result_repo = final_result_repo
        self.answer_sheet_repo = answer_sheet_repo
        self.exam_repo = exam_repo
        self.student_repo = student_repo
        self.sync_service = sync_service

    async def execute(
        self,
        exam_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None
    ) -> dict:
        """
        Retrieves paginated exam results, executing on-the-fly score synchronization where needed.
        """
        # 1. Fetch Exam
        exam = await self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise EntityNotFoundException(entity_type="Exam", entity_id=exam_id)

        # 2. Retrieve all answer sheets for this exam
        sheets = await self.answer_sheet_repo.get_all_by_exam_id(exam_id)
        
        # 3. Synchronize any verified sheets that do not have a FinalResult record
        sheet_map = {s.id: s for s in sheets}
        for s in sheets:
            # Check if verified or evaluation is completed
            if s.status in {AnswerSheetStatus.VERIFIED, AnswerSheetStatus.PUBLISHED}:
                # Try to find result
                res = await self.final_result_repo.get_by_answer_sheet_id(s.id)
                if not res:
                    try:
                        await self.sync_service.sync(s.id)
                    except Exception as sync_err:
                        logger.error(f"On-demand result aggregation failed for sheet {s.id}: {sync_err}")

        # 4. Fetch final results list
        results = await self.final_result_repo.get_by_exam_id(exam_id)

        # 5. Populate student details
        student_ids = list({r.student_id for r in results})
        students_list = []
        for s_id in student_ids:
            st = await self.student_repo.get_by_id(s_id)
            if st:
                students_list.append(st)
        
        student_map = {st.id: st for st in students_list}

        # 6. Map to dashboard item structures
        items = []
        for r in results:
            student = student_map.get(r.student_id)
            sheet = sheet_map.get(r.answer_sheet_id)

            if not student or not sheet:
                continue

            # Apply search criteria if present
            if search and search.strip():
                query = search.strip().lower()
                name_match = query in student.full_name.lower()
                number_match = query in student.student_number.lower()
                if not name_match and not number_match:
                    continue

            items.append({
                "student_id": r.student_id,
                "student_name": student.full_name,
                "student_number": student.student_number,
                "marks_obtained": r.total_marks_obtained,
                "percentage": r.percentage,
                "grade": r.grade,
                "pass_fail_status": r.pass_fail_status.value if hasattr(r.pass_fail_status, "value") else str(r.pass_fail_status),
                "verification_status": sheet.status.value if hasattr(sheet.status, "value") else str(sheet.status),
                "publication_status": "PUBLISHED" if r.is_published else "UNPUBLISHED"
            })

        # 7. Sort consistently (alphabetically by student name)
        items.sort(key=lambda x: x["student_name"].lower())

        # 8. Pagination slice
        total_items = len(items)
        total_pages = max(1, math.ceil(total_items / page_size))
        
        # Clamp page index
        current_page = max(1, min(page, total_pages))
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = items[start_idx:end_idx]

        return {
            "exam_id": str(exam_id),
            "exam_title": exam.title,
            "total_marks": exam.total_marks,
            "passing_marks": exam.passing_marks,
            "items": paginated_items,
            "total_items": total_items,
            "page": current_page,
            "page_size": page_size,
            "total_pages": total_pages
        }
