"""
application/use_cases/reports/generate_evaluation_report_pdf_use_case.py
"""

from __future__ import annotations
import uuid
from datetime import datetime

from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.student_repository import StudentRepository
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.rubric_criterion_repository import RubricCriterionRepository
from app.domain.repositories.criterion_evaluation_repository import CriterionEvaluationRepository
from app.domain.repositories.evaluation_revision_repository import EvaluationRevisionRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.reports.weasyprint_pdf_service import WeasyPrintPDFService

from app.domain.exceptions.domain_exception import EntityNotFoundException


class GenerateEvaluationReportPDFUseCase:
    """
    Use Case: Fetches evaluation data, scores, criteria breakdown, revisions list,
    and resolves student/exam details to render an evaluation detailed report PDF.
    """

    def __init__(
        self,
        evaluation_repo: EvaluationRepository,
        answer_sheet_repo: AnswerSheetRepository,
        student_repo: StudentRepository,
        exam_repo: ExamRepository,
        rubric_criterion_repo: RubricCriterionRepository,
        criterion_evaluation_repo: CriterionEvaluationRepository,
        evaluation_revision_repo: EvaluationRevisionRepository,
        user_repo: UserRepository,
        pdf_service: WeasyPrintPDFService
    ) -> None:
        self.evaluation_repo = evaluation_repo
        self.answer_sheet_repo = answer_sheet_repo
        self.student_repo = student_repo
        self.exam_repo = exam_repo
        self.rubric_criterion_repo = rubric_criterion_repo
        self.criterion_evaluation_repo = criterion_evaluation_repo
        self.evaluation_revision_repo = evaluation_revision_repo
        self.user_repo = user_repo
        self.pdf_service = pdf_service

    async def execute(self, evaluation_id: uuid.UUID) -> bytes:
        # 1. Fetch Evaluation
        evaluation = await self.evaluation_repo.get_by_id(evaluation_id)
        if not evaluation:
            raise EntityNotFoundException("Evaluation", evaluation_id)

        # 2. Fetch Answer Sheet
        answer_sheet = await self.answer_sheet_repo.get_by_id(evaluation.answer_sheet_id)
        if not answer_sheet:
            raise EntityNotFoundException("AnswerSheet", evaluation.answer_sheet_id)

        # 3. Fetch Student
        student = await self.student_repo.get_by_id(answer_sheet.student_id)
        student_name = student.full_name if student else "N/A"
        student_number = student.student_number if student else "N/A"

        # 4. Fetch Exam
        exam = await self.exam_repo.get_by_id(answer_sheet.exam_id)
        exam_title = exam.title if exam else "N/A"

        # 5. Fetch Criterion Evaluations
        criterion_evals = await self.criterion_evaluation_repo.get_by_evaluation_id(evaluation_id)
        
        criteria_list = []
        for ce in criterion_evals:
            # Resolve Rubric Criterion Name and Weight
            criterion = await self.rubric_criterion_repo.get_by_id(ce.rubric_criterion_id)
            crit_name = criterion.criterion_name if criterion else "General"
            crit_weight = criterion.weight if criterion else 1.0
            crit_max_marks = criterion.max_marks if criterion else ce.ai_score or ce.teacher_score or 10.0

            criteria_list.append({
                "criterion_name": crit_name,
                "weight": crit_weight,
                "max_marks": crit_max_marks,
                "ai_score": ce.ai_score,
                "teacher_score": ce.teacher_score,
                "ai_feedback": ce.ai_feedback,
                "teacher_feedback": ce.teacher_feedback
            })

        # 6. Fetch Revision History
        revisions = await self.evaluation_revision_repo.get_by_evaluation_id(evaluation_id)
        revision_list = []
        for rev in revisions:
            # Resolve reviewer name
            reviewer = await self.user_repo.get_by_id(rev.changed_by)
            rev_name = reviewer.full_name if reviewer else "System Officer"
            
            revision_list.append({
                "revision_number": rev.revision_number,
                "previous_score": rev.previous_score,
                "new_score": rev.new_score,
                "reason": rev.reason,
                "reviewer_name": rev_name,
                "timestamp": rev.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        # 7. Extract Explanation details
        exp = evaluation.explanation or {}
        
        context = {
            "institution_name": "AI Answer Evaluation System",
            "exam_title": exam_title,
            "evaluation_date": evaluation.created_at.strftime("%Y-%m-%d"),
            "student_name": student_name,
            "student_number": student_number,
            "is_verified": evaluation.is_verified,
            "verification_id": str(evaluation_id),
            "ai_score": evaluation.ai_score,
            "teacher_score": evaluation.teacher_score,
            "final_score": evaluation.final_score,
            "max_marks": evaluation.max_marks,
            "criteria_evaluations": criteria_list,
            "explanation_strengths": exp.get("strengths") or exp.get("strength"),
            "explanation_weaknesses": exp.get("weaknesses") or exp.get("weakness"),
            "explanation_missing_topics": exp.get("missing_topics") or exp.get("missing"),
            "explanation_suggestions": exp.get("suggestions") or exp.get("suggestion"),
            "revision_history": revision_list
        }

        # 8. Render to PDF
        return self.pdf_service.generate_pdf("evaluation_report.html", context)
