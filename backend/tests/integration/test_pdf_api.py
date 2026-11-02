"""
tests/integration/test_pdf_api.py — Integration Tests for PDF Result Reports REST API Endpoints
"""

from __future__ import annotations
import sys
import uuid
from datetime import datetime, timezone, date
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

# Mock WeasyPrint before importing router or app components
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
from app.domain.entities.exam import Exam
from app.domain.entities.subject import Subject
from app.core.constants import UserRole
from app.core.exceptions import unauthorized

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
    mock_html_class.return_value.write_pdf.return_value = b"%PDF-1.4 mock pdf bytes"
    mock_user.role = UserRole.TEACHER
    mock_user.email = "teacher@example.com"
    app.dependency_overrides[get_current_user] = override_current_user


# ── GET /results/students/{student_id}/transcript/pdf ───────────────────────────

def test_student_transcript_pdf_teacher_success():
    student_id = uuid.uuid4()
    mock_user.role = UserRole.TEACHER

    mock_history = {
        "student_id": str(student_id),
        "student_name": "Alice Student",
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
            }
        ]
    }

    with patch("app.application.use_cases.results.get_student_results_use_case.GetStudentResultsUseCase.execute", new_callable=AsyncMock) as mock_get_results:
        mock_get_results.return_value = mock_history

        response = client.get(f"/results/students/{student_id}/transcript/pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == f"attachment; filename=student_{student_id}_transcript.pdf"
        assert response.content.startswith(b"%PDF-")
        mock_get_results.assert_called_once_with(student_id, only_published=False)


def test_student_transcript_pdf_admin_success():
    student_id = uuid.uuid4()
    mock_user.role = UserRole.ADMIN

    mock_history = {
        "student_id": str(student_id),
        "student_name": "Alice Student",
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
            }
        ]
    }

    with patch("app.application.use_cases.results.get_student_results_use_case.GetStudentResultsUseCase.execute", new_callable=AsyncMock) as mock_get_results:
        mock_get_results.return_value = mock_history

        response = client.get(f"/results/students/{student_id}/transcript/pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == f"attachment; filename=student_{student_id}_transcript.pdf"
        assert response.content.startswith(b"%PDF-")
        mock_get_results.assert_called_once_with(student_id, only_published=False)


def test_student_transcript_pdf_own_student_success():
    student_id = uuid.uuid4()
    mock_user.role = "student"
    mock_user.email = "student@example.com"

    mock_student = Student(
        id=student_id,
        student_number="STU-001",
        full_name="Alice Student",
        email="student@example.com",
        class_section="A"
    )

    mock_history = {
        "student_id": str(student_id),
        "student_name": "Alice Student",
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
            }
        ]
    }

    with patch("app.infrastructure.persistence.repositories.sql_student_repository.SqlStudentRepository.get_by_email", new_callable=AsyncMock) as mock_get_email, \
         patch("app.application.use_cases.results.get_student_results_use_case.GetStudentResultsUseCase.execute", new_callable=AsyncMock) as mock_get_results:
        
        mock_get_email.return_value = mock_student
        mock_get_results.return_value = mock_history

        response = client.get(f"/results/students/{student_id}/transcript/pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == f"attachment; filename=student_{student_id}_transcript.pdf"
        assert response.content.startswith(b"%PDF-")
        mock_get_email.assert_called_once_with("student@example.com")
        mock_get_results.assert_called_once_with(student_id, only_published=True)


def test_student_transcript_pdf_other_student_forbidden():
    student_id = uuid.uuid4()
    other_student_id = uuid.uuid4()
    mock_user.role = "student"
    mock_user.email = "student@example.com"

    mock_student = Student(
        id=other_student_id,
        student_number="STU-001",
        full_name="Alice Student",
        email="student@example.com",
        class_section="A"
    )

    with patch("app.infrastructure.persistence.repositories.sql_student_repository.SqlStudentRepository.get_by_email", new_callable=AsyncMock) as mock_get_email:
        mock_get_email.return_value = mock_student

        response = client.get(f"/results/students/{student_id}/transcript/pdf")
        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied. Students can only access their own transcript."
        mock_get_email.assert_called_once_with("student@example.com")


def test_student_transcript_pdf_unauthenticated():
    student_id = uuid.uuid4()
    app.dependency_overrides[get_current_user] = override_unauthenticated
    response = client.get(f"/results/students/{student_id}/transcript/pdf")
    assert response.status_code == 401


# ── GET /results/exams/{exam_id}/report/pdf ───────────────────────────────────

def test_exam_report_pdf_teacher_success():
    exam_id = uuid.uuid4()
    subject_id = uuid.uuid4()
    mock_user.role = UserRole.TEACHER

    mock_exam = Exam(
        subject_id=subject_id,
        title="DSA Midterm",
        exam_date=date(2026, 6, 21),
        total_marks=100,
        passing_marks=40,
        created_by=uuid.uuid4(),
        id=exam_id
    )

    mock_subject = Subject(
        name="Data Structures",
        code="CS101",
        created_by=uuid.uuid4(),
        id=subject_id
    )

    mock_exam_results = {
        "exam_id": str(exam_id),
        "exam_title": "DSA Midterm",
        "total_marks": 100,
        "passing_marks": 40,
        "items": [
            {
                "student_id": uuid.uuid4(),
                "student_name": "Alice Student",
                "student_number": "STU-001",
                "marks_obtained": 80.0,
                "percentage": 80.0,
                "grade": "A+",
                "pass_fail_status": "PASS",
                "verification_status": "VERIFIED",
                "publication_status": "PUBLISHED"
            }
        ],
        "total_items": 1,
        "page": 1,
        "page_size": 1000000,
        "total_pages": 1
    }

    with patch("app.application.use_cases.results.get_exam_results_use_case.GetExamResultsUseCase.execute", new_callable=AsyncMock) as mock_get_results, \
         patch("app.infrastructure.persistence.repositories.sql_exam_repository.SqlExamRepository.get_by_id", new_callable=AsyncMock) as mock_get_exam, \
         patch("app.infrastructure.persistence.repositories.sql_subject_repository.SqlSubjectRepository.get_by_id", new_callable=AsyncMock) as mock_get_subject:
        
        mock_get_results.return_value = mock_exam_results
        mock_get_exam.return_value = mock_exam
        mock_get_subject.return_value = mock_subject

        response = client.get(f"/results/exams/{exam_id}/report/pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == f"attachment; filename=exam_{exam_id}_report.pdf"
        assert response.content.startswith(b"%PDF-")


def test_exam_report_pdf_admin_success():
    exam_id = uuid.uuid4()
    subject_id = uuid.uuid4()
    mock_user.role = UserRole.ADMIN

    mock_exam = Exam(
        subject_id=subject_id,
        title="DSA Midterm",
        exam_date=date(2026, 6, 21),
        total_marks=100,
        passing_marks=40,
        created_by=uuid.uuid4(),
        id=exam_id
    )

    mock_subject = Subject(
        name="Data Structures",
        code="CS101",
        created_by=uuid.uuid4(),
        id=subject_id
    )

    mock_exam_results = {
        "exam_id": str(exam_id),
        "exam_title": "DSA Midterm",
        "total_marks": 100,
        "passing_marks": 40,
        "items": [
            {
                "student_id": uuid.uuid4(),
                "student_name": "Alice Student",
                "student_number": "STU-001",
                "marks_obtained": 80.0,
                "percentage": 80.0,
                "grade": "A+",
                "pass_fail_status": "PASS",
                "verification_status": "VERIFIED",
                "publication_status": "PUBLISHED"
            }
        ],
        "total_items": 1,
        "page": 1,
        "page_size": 1000000,
        "total_pages": 1
    }

    with patch("app.application.use_cases.results.get_exam_results_use_case.GetExamResultsUseCase.execute", new_callable=AsyncMock) as mock_get_results, \
         patch("app.infrastructure.persistence.repositories.sql_exam_repository.SqlExamRepository.get_by_id", new_callable=AsyncMock) as mock_get_exam, \
         patch("app.infrastructure.persistence.repositories.sql_subject_repository.SqlSubjectRepository.get_by_id", new_callable=AsyncMock) as mock_get_subject:
        
        mock_get_results.return_value = mock_exam_results
        mock_get_exam.return_value = mock_exam
        mock_get_subject.return_value = mock_subject

        response = client.get(f"/results/exams/{exam_id}/report/pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == f"attachment; filename=exam_{exam_id}_report.pdf"
        assert response.content.startswith(b"%PDF-")


def test_exam_report_pdf_student_forbidden():
    exam_id = uuid.uuid4()
    mock_user.role = "student"

    response = client.get(f"/results/exams/{exam_id}/report/pdf")
    assert response.status_code == 403


def test_exam_report_pdf_unauthenticated():
    exam_id = uuid.uuid4()
    app.dependency_overrides[get_current_user] = override_unauthenticated
    response = client.get(f"/results/exams/{exam_id}/report/pdf")
    assert response.status_code == 401
