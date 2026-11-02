"""
tests/unit/application/test_evaluation_report_pdf.py — Unit Tests for Evaluation Report PDF Use Case
"""

from __future__ import annotations
import sys
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Mock WeasyPrint HTML class to prevent GTK library load error
if 'weasyprint' in sys.modules:
    mock_weasyprint = sys.modules['weasyprint']
    mock_html_class = mock_weasyprint.HTML
else:
    mock_weasyprint = MagicMock()
    mock_html_class = MagicMock()
    mock_weasyprint.HTML = mock_html_class
    sys.modules['weasyprint'] = mock_weasyprint

import pytest
from app.application.use_cases.reports.generate_evaluation_report_pdf_use_case import GenerateEvaluationReportPDFUseCase
from app.infrastructure.reports.weasyprint_pdf_service import WeasyPrintPDFService

# Repositories interfaces/concrete mocks
from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.student_repository import StudentRepository
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.rubric_criterion_repository import RubricCriterionRepository
from app.domain.repositories.criterion_evaluation_repository import CriterionEvaluationRepository
from app.domain.repositories.evaluation_revision_repository import EvaluationRevisionRepository
from app.domain.repositories.user_repository import UserRepository


@pytest.fixture
def mock_pdf_service():
    service = WeasyPrintPDFService()
    mock_html_class.return_value.write_pdf.return_value = b"%PDF-1.4 mock evaluation report bytes"
    return service


@pytest.mark.asyncio
async def test_generate_evaluation_report_pdf_success(mock_pdf_service):
    evaluation_id = uuid.uuid4()
    answer_sheet_id = uuid.uuid4()
    student_id = uuid.uuid4()
    exam_id = uuid.uuid4()
    rubric_criterion_id = uuid.uuid4()
    changed_by_user_id = uuid.uuid4()

    # Mocks
    mock_eval = MagicMock()
    mock_eval.id = evaluation_id
    mock_eval.answer_sheet_id = answer_sheet_id
    mock_eval.ai_score = 75.0
    mock_eval.teacher_score = 80.0
    mock_eval.final_score = 80.0
    mock_eval.max_marks = 100.0
    mock_eval.is_verified = True
    mock_eval.created_at = datetime(2026, 6, 21)
    mock_eval.explanation = {
        "strengths": "Strong core logic.",
        "weaknesses": "Missing boundary cases.",
        "missing_topics": "Thread synchronization details.",
        "suggestions": "Review multi-threading primitives."
    }

    mock_sheet = MagicMock()
    mock_sheet.id = answer_sheet_id
    mock_sheet.student_id = student_id
    mock_sheet.exam_id = exam_id

    mock_student = MagicMock()
    mock_student.id = student_id
    mock_student.full_name = "Alice Vance"
    mock_student.student_number = "STU-001"

    mock_exam = MagicMock()
    mock_exam.id = exam_id
    mock_exam.title = "Operating Systems Final"

    mock_crit_eval = MagicMock()
    mock_crit_eval.rubric_criterion_id = rubric_criterion_id
    mock_crit_eval.ai_score = 15.0
    mock_crit_eval.teacher_score = 18.0
    mock_crit_eval.ai_feedback = "Good, minor spelling issues"
    mock_crit_eval.teacher_feedback = "Agreed, solid answer"

    mock_rubric_criterion = MagicMock()
    mock_rubric_criterion.id = rubric_criterion_id
    mock_rubric_criterion.criterion_name = "Correctness & Completeness"
    mock_rubric_criterion.weight = 0.5
    mock_rubric_criterion.max_marks = 20.0

    mock_revision = MagicMock()
    mock_revision.revision_number = 1
    mock_revision.previous_score = 75.0
    mock_revision.new_score = 80.0
    mock_revision.reason = "Manual override after teacher verification"
    mock_revision.changed_by = changed_by_user_id
    mock_revision.created_at = datetime(2026, 6, 21, 14, 0, 0)

    mock_user = MagicMock()
    mock_user.id = changed_by_user_id
    mock_user.full_name = "Dr. Robert Smith"

    # Repository Mocks setup
    evaluation_repo = MagicMock(spec=EvaluationRepository)
    evaluation_repo.get_by_id = AsyncMock(return_value=mock_eval)

    answer_sheet_repo = MagicMock(spec=AnswerSheetRepository)
    answer_sheet_repo.get_by_id = AsyncMock(return_value=mock_sheet)

    student_repo = MagicMock(spec=StudentRepository)
    student_repo.get_by_id = AsyncMock(return_value=mock_student)

    exam_repo = MagicMock(spec=ExamRepository)
    exam_repo.get_by_id = AsyncMock(return_value=mock_exam)

    rubric_criterion_repo = MagicMock(spec=RubricCriterionRepository)
    rubric_criterion_repo.get_by_id = AsyncMock(return_value=mock_rubric_criterion)

    criterion_evaluation_repo = MagicMock(spec=CriterionEvaluationRepository)
    criterion_evaluation_repo.get_by_evaluation_id = AsyncMock(return_value=[mock_crit_eval])

    evaluation_revision_repo = MagicMock(spec=EvaluationRevisionRepository)
    evaluation_revision_repo.get_by_evaluation_id = AsyncMock(return_value=[mock_revision])

    user_repo = MagicMock(spec=UserRepository)
    user_repo.get_by_id = AsyncMock(return_value=mock_user)

    use_case = GenerateEvaluationReportPDFUseCase(
        evaluation_repo=evaluation_repo,
        answer_sheet_repo=answer_sheet_repo,
        student_repo=student_repo,
        exam_repo=exam_repo,
        rubric_criterion_repo=rubric_criterion_repo,
        criterion_evaluation_repo=criterion_evaluation_repo,
        evaluation_revision_repo=evaluation_revision_repo,
        user_repo=user_repo,
        pdf_service=mock_pdf_service
    )

    with patch.object(mock_pdf_service, 'generate_pdf', return_value=b"%PDF-1.4 mock evaluation report bytes") as mock_generate:
        pdf_bytes = await use_case.execute(evaluation_id=evaluation_id)
        
        assert pdf_bytes == b"%PDF-1.4 mock evaluation report bytes"
        mock_generate.assert_called_once()
        
        template_name, context = mock_generate.call_args[0]
        assert template_name == "evaluation_report.html"
        
        # Verify context details mapping
        assert context["institution_name"] == "AI Answer Evaluation System"
        assert context["exam_title"] == "Operating Systems Final"
        assert context["evaluation_date"] == "2026-06-21"
        assert context["student_name"] == "Alice Vance"
        assert context["student_number"] == "STU-001"
        assert context["is_verified"] is True
        assert context["verification_id"] == str(evaluation_id)
        assert context["ai_score"] == 75.0
        assert context["teacher_score"] == 80.0
        assert context["final_score"] == 80.0
        assert context["max_marks"] == 100.0
        
        # Verify Criterion breakdown mapping
        assert len(context["criteria_evaluations"]) == 1
        ce_mapped = context["criteria_evaluations"][0]
        assert ce_mapped["criterion_name"] == "Correctness & Completeness"
        assert ce_mapped["weight"] == 0.5
        assert ce_mapped["max_marks"] == 20.0
        assert ce_mapped["ai_score"] == 15.0
        assert ce_mapped["teacher_score"] == 18.0
        assert ce_mapped["ai_feedback"] == "Good, minor spelling issues"
        assert ce_mapped["teacher_feedback"] == "Agreed, solid answer"
        
        # Verify Revision History mapping
        assert len(context["revision_history"]) == 1
        rev_mapped = context["revision_history"][0]
        assert rev_mapped["revision_number"] == 1
        assert rev_mapped["previous_score"] == 75.0
        assert rev_mapped["new_score"] == 80.0
        assert rev_mapped["reason"] == "Manual override after teacher verification"
        assert rev_mapped["reviewer_name"] == "Dr. Robert Smith"
        assert rev_mapped["timestamp"] == "2026-06-21 14:00:00"

        # Verify AI Explanation section
        assert context["explanation_strengths"] == "Strong core logic."
        assert context["explanation_weaknesses"] == "Missing boundary cases."
        assert context["explanation_missing_topics"] == "Thread synchronization details."
        assert context["explanation_suggestions"] == "Review multi-threading primitives."
