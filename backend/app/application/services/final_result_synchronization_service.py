"""
application/services/final_result_synchronization_service.py — FinalResult Synchronization Service
"""

from __future__ import annotations
import uuid
import logging
from datetime import datetime, timezone

from app.domain.entities.final_result import FinalResult
from app.domain.repositories.final_result_repository import FinalResultRepository
from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.repositories.exam_repository import ExamRepository

from app.core.constants import PassFailStatus, GRADE_BOUNDARIES
from app.domain.exceptions.domain_exception import EntityNotFoundException

logger = logging.getLogger(__name__)


class FinalResultSynchronizationService:
    """
    Service responsible for computing final marks, percentage, letter grade,
    and pass/fail status of a student answer sheet, and writing the result to final_results.
    """

    def __init__(
        self,
        final_result_repo: FinalResultRepository,
        evaluation_repo: EvaluationRepository,
        answer_sheet_repo: AnswerSheetRepository,
        question_repo: QuestionRepository,
        exam_repo: ExamRepository
    ) -> None:
        self.final_result_repo = final_result_repo
        self.evaluation_repo = evaluation_repo
        self.answer_sheet_repo = answer_sheet_repo
        self.question_repo = question_repo
        self.exam_repo = exam_repo

    async def sync(self, answer_sheet_id: uuid.UUID) -> FinalResult:
        """
        Synchronizes score aggregations from question evaluations to the final result entry.
        """
        now = datetime.now(timezone.utc)

        # 1. Fetch Answer Sheet
        sheet = await self.answer_sheet_repo.get_by_id(answer_sheet_id)
        if not sheet:
            raise EntityNotFoundException(entity_type="AnswerSheet", entity_id=answer_sheet_id)

        # 2. Fetch Exam
        exam = await self.exam_repo.get_by_id(sheet.exam_id)
        if not exam:
            raise EntityNotFoundException(entity_type="Exam", entity_id=sheet.exam_id)

        # 3. Fetch Evaluations for this sheet
        evaluations = await self.evaluation_repo.get_by_answer_sheet_id(answer_sheet_id)

        # 4. Fetch Exam Questions to calculate total possible marks
        questions = await self.question_repo.get_by_exam_id(sheet.exam_id)
        total_possible = sum(q.marks for q in questions)
        if total_possible <= 0:
            total_possible = exam.total_marks

        # 5. Compute marks obtained
        # Use teacher verified score if verified, otherwise fallback to AI score
        total_obtained = 0.0
        for ev in evaluations:
            if ev.is_verified and ev.teacher_score is not None:
                total_obtained += ev.teacher_score
            else:
                total_obtained += ev.ai_score or 0.0

        # Cap obtained marks to possible marks
        if total_obtained > total_possible:
            total_obtained = float(total_possible)

        # 6. Calculate percentage & grade
        percentage = (total_obtained / total_possible) * 100.0 if total_possible > 0 else 0.0
        
        grade = "F"
        for threshold, grade_enum in GRADE_BOUNDARIES:
            if percentage >= threshold:
                grade = grade_enum.value if hasattr(grade_enum, "value") else str(grade_enum)
                break

        # 7. Determine Pass/Fail Status
        pass_fail = PassFailStatus.PASS if total_obtained >= exam.passing_marks else PassFailStatus.FAIL

        # 8. Check if FinalResult already exists
        final_result = await self.final_result_repo.get_by_answer_sheet_id(answer_sheet_id)
        if final_result:
            final_result.total_marks_obtained = total_obtained
            final_result.total_marks_possible = total_possible
            final_result.percentage = percentage
            final_result.grade = grade
            final_result.pass_fail_status = pass_fail
            final_result.updated_at = now
        else:
            final_result = FinalResult(
                id=uuid.uuid4(),
                answer_sheet_id=answer_sheet_id,
                student_id=sheet.student_id,
                exam_id=sheet.exam_id,
                total_marks_obtained=total_obtained,
                total_marks_possible=total_possible,
                percentage=percentage,
                grade=grade,
                pass_fail_status=pass_fail,
                is_published=False,
                created_at=now,
                updated_at=now
            )

        saved = await self.final_result_repo.save(final_result)
        logger.info(
            f"Synced FinalResult for sheet {answer_sheet_id}. Total: {total_obtained}/{total_possible} ({percentage:.1f}%), Grade: {grade}, Status: {pass_fail}"
        )
        return saved
