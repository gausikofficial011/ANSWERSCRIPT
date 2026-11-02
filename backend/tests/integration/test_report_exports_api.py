"""
tests/integration/test_report_exports_api.py — Integration Tests for Report Exports REST API Router
"""

from __future__ import annotations
import sys
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

# Mock WeasyPrint HTML class to prevent GTK library load error
if 'weasyprint' in sys.modules:
    mock_weasyprint = sys.modules['weasyprint']
    mock_html_class = mock_weasyprint.HTML
else:
    mock_weasyprint = MagicMock()
    mock_html_class = MagicMock()
    mock_weasyprint.HTML = mock_html_class
    sys.modules['weasyprint'] = mock_weasyprint

from app.api.v1.router import api_router
from app.api.v1.dependencies.auth import get_current_user
from app.infrastructure.persistence.database import get_db_session
from app.domain.entities.user import User
from app.domain.entities.student import Student
from app.core.constants import UserRole
from app.core.exceptions import unauthorized
from app.infrastructure.reports.report_registry import report_registry

app = FastAPI()
app.include_router(api_router)

mock_db = MagicMock(spec=AsyncSession)
mock_user = User(
    id=uuid.uuid4(),
    email="teacher@example.com",
    username="teacher1",
    hashed_password="hash",
    full_name="John Teacher",
    role=UserRole.TEACHER,
    is_active=True,
    created_at=datetime.now(timezone.utc)
)

def get_mock_db():
    yield mock_db

async def override_current_user():
    return mock_user

async def override_unauthenticated():
    raise unauthorized("Invalid credentials")

app.dependency_overrides[get_db_session] = get_mock_db
app.dependency_overrides[get_current_user] = override_current_user
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_mocks_and_overrides():
    mock_db.reset_mock()
    mock_html_class.reset_mock()
    mock_html_class.return_value.write_pdf.return_value = b"%PDF-1.4 mock report bytes"
    mock_user.role = UserRole.TEACHER
    mock_user.email = "teacher@example.com"
    app.dependency_overrides[get_current_user] = override_current_user
    report_registry.clear()


# ── GET /evaluations/{id}/report/pdf ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_evaluation_report_pdf_teacher_success():
    evaluation_id = uuid.uuid4()
    mock_user.role = UserRole.TEACHER
    
    mock_evaluation = MagicMock()
    mock_evaluation.answer_sheet_id = uuid.uuid4()
    
    # Mock SqlEvaluationRepository get_by_id and execute of generate use case
    with patch("app.infrastructure.persistence.repositories.sql_evaluation_repository.SqlEvaluationRepository.get_by_id", new_callable=AsyncMock) as mock_get_eval, \
         patch("app.application.use_cases.reports.generate_evaluation_report_pdf_use_case.GenerateEvaluationReportPDFUseCase.execute", new_callable=AsyncMock) as mock_execute:
        
        mock_get_eval.return_value = mock_evaluation
        mock_execute.return_value = b"%PDF-1.4 mock evaluation report bytes"

        response = client.get(f"/evaluations/{evaluation_id}/report/pdf")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == f"attachment; filename=evaluation_{evaluation_id}_report.pdf"
        assert response.content.startswith(b"%PDF-")
        
        # Verify registered in ReportRegistry
        registered = report_registry.get_all()
        assert len(registered) == 1
        assert registered[0].report_type == "evaluation_report"
        assert registered[0].metadata["evaluation_id"] == str(evaluation_id)


@pytest.mark.asyncio
async def test_evaluation_report_pdf_admin_success():
    evaluation_id = uuid.uuid4()
    mock_user.role = UserRole.ADMIN
    
    mock_evaluation = MagicMock()
    mock_evaluation.answer_sheet_id = uuid.uuid4()
    
    with patch("app.infrastructure.persistence.repositories.sql_evaluation_repository.SqlEvaluationRepository.get_by_id", new_callable=AsyncMock) as mock_get_eval, \
         patch("app.application.use_cases.reports.generate_evaluation_report_pdf_use_case.GenerateEvaluationReportPDFUseCase.execute", new_callable=AsyncMock) as mock_execute:
        
        mock_get_eval.return_value = mock_evaluation
        mock_execute.return_value = b"%PDF-1.4 mock evaluation report bytes"

        response = client.get(f"/evaluations/{evaluation_id}/report/pdf")
        
        assert response.status_code == 200
        assert response.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_evaluation_report_pdf_own_student_success():
    evaluation_id = uuid.uuid4()
    student_id = uuid.uuid4()
    answer_sheet_id = uuid.uuid4()
    
    mock_user.role = "student"
    mock_user.email = "student@example.com"
    
    mock_evaluation = MagicMock()
    mock_evaluation.answer_sheet_id = answer_sheet_id
    
    mock_answer_sheet = MagicMock()
    mock_answer_sheet.student_id = student_id
    
    mock_student = Student(
        id=student_id,
        student_number="STU-001",
        full_name="Alice Student",
        email="student@example.com",
        class_section="A"
    )
    
    with patch("app.infrastructure.persistence.repositories.sql_evaluation_repository.SqlEvaluationRepository.get_by_id", new_callable=AsyncMock) as mock_get_eval, \
         patch("app.infrastructure.persistence.repositories.sql_answer_sheet_repository.SqlAnswerSheetRepository.get_by_id", new_callable=AsyncMock) as mock_get_sheet, \
         patch("app.infrastructure.persistence.repositories.sql_student_repository.SqlStudentRepository.get_by_email", new_callable=AsyncMock) as mock_get_student, \
         patch("app.application.use_cases.reports.generate_evaluation_report_pdf_use_case.GenerateEvaluationReportPDFUseCase.execute", new_callable=AsyncMock) as mock_execute:
        
        mock_get_eval.return_value = mock_evaluation
        mock_get_sheet.return_value = mock_answer_sheet
        mock_get_student.return_value = mock_student
        mock_execute.return_value = b"%PDF-1.4 mock evaluation report bytes"

        response = client.get(f"/evaluations/{evaluation_id}/report/pdf")
        
        assert response.status_code == 200
        assert response.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_evaluation_report_pdf_other_student_forbidden():
    evaluation_id = uuid.uuid4()
    student_id = uuid.uuid4()
    other_student_id = uuid.uuid4()
    answer_sheet_id = uuid.uuid4()
    
    mock_user.role = "student"
    mock_user.email = "student@example.com"
    
    mock_evaluation = MagicMock()
    mock_evaluation.answer_sheet_id = answer_sheet_id
    
    mock_answer_sheet = MagicMock()
    mock_answer_sheet.student_id = student_id
    
    # User student resolves to other_student_id (different from answer_sheet's student_id)
    mock_student = Student(
        id=other_student_id,
        student_number="STU-002",
        full_name="Bob Student",
        email="student@example.com",
        class_section="A"
    )
    
    with patch("app.infrastructure.persistence.repositories.sql_evaluation_repository.SqlEvaluationRepository.get_by_id", new_callable=AsyncMock) as mock_get_eval, \
         patch("app.infrastructure.persistence.repositories.sql_answer_sheet_repository.SqlAnswerSheetRepository.get_by_id", new_callable=AsyncMock) as mock_get_sheet, \
         patch("app.infrastructure.persistence.repositories.sql_student_repository.SqlStudentRepository.get_by_email", new_callable=AsyncMock) as mock_get_student:
        
        mock_get_eval.return_value = mock_evaluation
        mock_get_sheet.return_value = mock_answer_sheet
        mock_get_student.return_value = mock_student

        response = client.get(f"/evaluations/{evaluation_id}/report/pdf")
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]


@pytest.mark.asyncio
async def test_evaluation_report_pdf_unauthenticated():
    evaluation_id = uuid.uuid4()
    app.dependency_overrides[get_current_user] = override_unauthenticated
    response = client.get(f"/evaluations/{evaluation_id}/report/pdf")
    assert response.status_code == 401


# ── GET /plagiarism/reports/{id}/export/pdf ───────────────────────────────────

@pytest.mark.asyncio
async def test_plagiarism_report_pdf_teacher_success():
    report_id = uuid.uuid4()
    mock_user.role = UserRole.TEACHER
    
    mock_report = MagicMock()
    
    with patch("app.infrastructure.persistence.repositories.sql_plagiarism_repository.SqlPlagiarismRepository.get_by_id", new_callable=AsyncMock) as mock_get_report, \
         patch("app.application.use_cases.reports.generate_plagiarism_report_pdf_use_case.GeneratePlagiarismReportPDFUseCase.execute", new_callable=AsyncMock) as mock_execute:
        
        mock_get_report.return_value = mock_report
        mock_execute.return_value = b"%PDF-1.4 mock plagiarism report bytes"

        response = client.get(f"/plagiarism/reports/{report_id}/export/pdf")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == f"attachment; filename=plagiarism_report_{report_id}.pdf"
        assert response.content.startswith(b"%PDF-")
        
        # Verify registered in ReportRegistry
        registered = report_registry.get_all()
        assert len(registered) == 1
        assert registered[0].report_type == "plagiarism_report"
        assert registered[0].metadata["report_id"] == str(report_id)


@pytest.mark.asyncio
async def test_plagiarism_report_pdf_admin_success():
    report_id = uuid.uuid4()
    mock_user.role = UserRole.ADMIN
    
    mock_report = MagicMock()
    
    with patch("app.infrastructure.persistence.repositories.sql_plagiarism_repository.SqlPlagiarismRepository.get_by_id", new_callable=AsyncMock) as mock_get_report, \
         patch("app.application.use_cases.reports.generate_plagiarism_report_pdf_use_case.GeneratePlagiarismReportPDFUseCase.execute", new_callable=AsyncMock) as mock_execute:
        
        mock_get_report.return_value = mock_report
        mock_execute.return_value = b"%PDF-1.4 mock plagiarism report bytes"

        response = client.get(f"/plagiarism/reports/{report_id}/export/pdf")
        
        assert response.status_code == 200
        assert response.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_plagiarism_report_pdf_student_forbidden():
    report_id = uuid.uuid4()
    mock_user.role = "student"
    
    response = client.get(f"/plagiarism/reports/{report_id}/export/pdf")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_plagiarism_report_pdf_unauthenticated():
    report_id = uuid.uuid4()
    app.dependency_overrides[get_current_user] = override_unauthenticated
    response = client.get(f"/plagiarism/reports/{report_id}/export/pdf")
    assert response.status_code == 401
