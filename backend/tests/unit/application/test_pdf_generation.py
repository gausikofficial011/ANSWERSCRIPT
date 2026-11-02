"""
tests/unit/application/test_pdf_generation.py — Unit Tests for PDF Generation Use Cases and Services
"""

from __future__ import annotations
import sys
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

# Mock the entire weasyprint module to avoid GTK3 library load exceptions
if 'weasyprint' in sys.modules:
    mock_weasyprint = sys.modules['weasyprint']
    mock_html_class = mock_weasyprint.HTML
else:
    mock_weasyprint = MagicMock()
    mock_html_class = MagicMock()
    mock_weasyprint.HTML = mock_html_class
    sys.modules['weasyprint'] = mock_weasyprint

import pytest
from app.application.use_cases.results.generate_student_transcript_pdf_use_case import GenerateStudentTranscriptPDFUseCase
from app.application.use_cases.results.generate_exam_report_pdf_use_case import GenerateExamReportPDFUseCase
from app.application.use_cases.results.get_student_results_use_case import GetStudentResultsUseCase
from app.application.use_cases.results.get_exam_results_use_case import GetExamResultsUseCase
from app.infrastructure.reports.weasyprint_pdf_service import WeasyPrintPDFService
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.subject_repository import SubjectRepository


@pytest.fixture
def mock_pdf_service():
    service = WeasyPrintPDFService()
    # Mock render and write_pdf calls
    mock_html_class.return_value.write_pdf.return_value = b"%PDF-1.4 mock pdf bytes"
    return service


@pytest.mark.asyncio
async def test_generate_student_transcript_pdf_calculations(mock_pdf_service):
    mock_get_student = MagicMock(spec=GetStudentResultsUseCase)
    mock_get_student.execute = AsyncMock(return_value={
        "student_id": str(uuid.uuid4()),
        "student_name": "Alice Vance",
        "student_number": "STU-001",
        "class_section": "A",
        "history": [
            {
                "exam_id": uuid.uuid4(),
                "exam_title": "DSA Midterm",
                "subject_name": "Data Structures",
                "percentage": 90.0,
                "grade": "O",
                "pass_fail_status": "PASS",
                "published_status": "PUBLISHED"
            },
            {
                "exam_id": uuid.uuid4(),
                "exam_title": "OS Final",
                "subject_name": "Operating Systems",
                "percentage": 80.0,
                "grade": "A+",
                "pass_fail_status": "PASS",
                "published_status": "PUBLISHED"
            },
            {
                "exam_id": uuid.uuid4(),
                "exam_title": "Networks Quiz",
                "subject_name": "Networking",
                "percentage": 95.0,
                "grade": "O",
                "pass_fail_status": "PASS",
                "published_status": "UNPUBLISHED" # Draft result, must be ignored in transcript calculations
            }
        ]
    })

    use_case = GenerateStudentTranscriptPDFUseCase(mock_get_student, mock_pdf_service)
    student_id = uuid.uuid4()
    
    with patch.object(mock_pdf_service, 'generate_pdf', return_value=b"%PDF-1.4 mock pdf bytes") as mock_generate:
        pdf_bytes = await use_case.execute(student_id)
        
        # Verify call arguments to PDF Generator
        mock_generate.assert_called_once()
        template_name, context = mock_generate.call_args[0]
        assert template_name == "transcript.html"
        
        # Verify stats calculations
        assert context["student_name"] == "Alice Vance"
        assert context["total_exams"] == 2 # Only PUBLISHED
        assert context["average_percentage"] == 85.0 # (90 + 80) / 2
        assert context["highest_percentage"] == 90.0
        assert context["lowest_percentage"] == 80.0
        assert context["pass_rate"] == 100.0
        assert len(context["history"]) == 2
        assert pdf_bytes.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_generate_exam_report_pdf_calculations(mock_pdf_service):
    mock_get_exam = MagicMock(spec=GetExamResultsUseCase)
    mock_get_exam.execute = AsyncMock(return_value={
        "exam_id": str(uuid.uuid4()),
        "exam_title": "DSA Midterm",
        "total_marks": 100,
        "passing_marks": 40,
        "items": [
            {
                "student_id": uuid.uuid4(),
                "student_name": "Alice Vance",
                "student_number": "STU-001",
                "marks_obtained": 80.0,
                "percentage": 80.0,
                "grade": "A+",
                "pass_fail_status": "PASS",
                "verification_status": "VERIFIED",
                "publication_status": "PUBLISHED"
            },
            {
                "student_id": uuid.uuid4(),
                "student_name": "Bob Miller",
                "student_number": "STU-002",
                "marks_obtained": 30.0,
                "percentage": 30.0,
                "grade": "F",
                "pass_fail_status": "FAIL",
                "verification_status": "VERIFIED",
                "publication_status": "PUBLISHED"
            }
        ]
    })

    mock_exam_repo = MagicMock(spec=ExamRepository)
    mock_exam = MagicMock()
    mock_exam.subject_id = uuid.uuid4()
    mock_exam_repo.get_by_id = AsyncMock(return_value=mock_exam)
    
    mock_subject_repo = MagicMock(spec=SubjectRepository)
    mock_subject = MagicMock()
    mock_subject.name = "Computer Science"
    mock_subject.code = "CS202"
    mock_subject_repo.get_by_id = AsyncMock(return_value=mock_subject)

    use_case = GenerateExamReportPDFUseCase(
        get_exam_results_use_case=mock_get_exam,
        exam_repo=mock_exam_repo,
        subject_repo=mock_subject_repo,
        pdf_service=mock_pdf_service
    )
    
    exam_id = uuid.uuid4()

    with patch.object(mock_pdf_service, 'generate_pdf', return_value=b"%PDF-1.4 mock pdf bytes") as mock_generate:
        pdf_bytes = await use_case.execute(exam_id)
        
        mock_generate.assert_called_once()
        template_name, context = mock_generate.call_args[0]
        assert template_name == "exam_report.html"
        
        # Verify stats calculations
        assert context["total_candidates"] == 2
        assert context["average_percentage"] == 55.0 # (80 + 30) / 2
        assert context["pass_rate"] == 50.0
        assert context["fail_rate"] == 50.0
        assert context["subject_name"] == "Computer Science (CS202)"
        assert pdf_bytes.startswith(b"%PDF-")


def test_weasyprint_pdf_service_rendering(mock_pdf_service):
    # Verify Jinja environment loaded templates correctly
    assert mock_pdf_service.env.get_template("transcript.html") is not None
    assert mock_pdf_service.env.get_template("exam_report.html") is not None

    # Test PDF generation wrapper compiles context
    context = {
        "student_name": "Test Student",
        "student_number": "STU-001",
        "class_section": "A",
        "current_date": "2026-06-21",
        "total_exams": 0,
        "average_percentage": 0.0,
        "highest_percentage": 0.0,
        "lowest_percentage": 0.0,
        "pass_rate": 0.0,
        "history": [],
        "verification_id": "1234"
    }
    mock_html_class.reset_mock()
    pdf_bytes = mock_pdf_service.generate_pdf("transcript.html", context)
    assert pdf_bytes == b"%PDF-1.4 mock pdf bytes"
    mock_html_class.assert_called_once()
