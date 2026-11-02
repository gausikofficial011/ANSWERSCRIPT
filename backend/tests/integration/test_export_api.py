"""
tests/integration/test_export_api.py — Integration Tests for CSV Results Exports REST API Endpoints
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io

from app.api.v1.router import api_router
from app.api.v1.dependencies.auth import get_current_user
from app.infrastructure.persistence.database import get_db_session
from app.domain.entities.user import User
from app.core.constants import UserRole, PassFailStatus, AnswerSheetStatus
from app.core.exceptions import unauthorized

app = FastAPI()
app.include_router(api_router)

mock_db = MagicMock(spec=AsyncSession)
mock_user = User(
    id=uuid.uuid4(),
    email="teacher@example.com",
    username="teacher1",
    hashed_password="hash",
    full_name="John Doe",
    role=UserRole.TEACHER,
    is_active=True,
    created_at=datetime.now(timezone.utc)
)


def get_mock_db():
    yield mock_db


async def override_teacher_user():
    return mock_user


async def override_student_user():
    return User(
        id=uuid.uuid4(),
        email="student@example.com",
        username="student1",
        hashed_password="hash",
        full_name="Alice Student",
        role="student",
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )


async def override_unauthenticated():
    raise unauthorized("Invalid credentials")


# Default dependencies overrides
app.dependency_overrides[get_db_session] = get_mock_db
app.dependency_overrides[get_current_user] = override_teacher_user
client = TestClient(app)


async def mock_execute(query, *args, **kwargs):
    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.student_model import StudentModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    
    model_class = None
    if hasattr(query, "column_descriptions") and len(query.column_descriptions) > 0:
        model_class = query.column_descriptions[0].get("entity")

    entity_id = None
    if hasattr(query, "compile"):
        try:
            params = query.compile().params
            for k, val in params.items():
                if isinstance(val, uuid.UUID):
                    entity_id = val
                    break
        except Exception:
            pass

    if model_class and entity_id:
        try:
            model = await mock_db.get(model_class, entity_id)
            if model:
                result = MagicMock()
                result.scalar_one_or_none.return_value = model
                result.scalar_one.return_value = 1
                result.scalar.return_value = 1
                result.scalars.return_value.first.return_value = model
                result.scalars.return_value.all.return_value = [model]
                return result
        except Exception:
            pass

    return mock_db.execute.return_value


@pytest.fixture(autouse=True)
def reset_mocks_and_overrides():
    mock_db.reset_mock()
    mock_db.execute = AsyncMock(side_effect=mock_execute)
    
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_execute_result.scalar_one.return_value = 0
    mock_execute_result.scalar.return_value = 0
    mock_execute_result.scalars.return_value.first.return_value = None
    mock_execute_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_execute_result

    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.get = AsyncMock()
    mock_db.merge = AsyncMock()
    mock_user.role = UserRole.TEACHER
    app.dependency_overrides[get_current_user] = override_teacher_user



# ── GET /results/exams/{exam_id}/export/csv ───────────────────────────────────

def test_export_exam_results_csv_success():
    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.student_model import StudentModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.final_result_model import FinalResultModel

    exam_id = uuid.uuid4()
    student_id = uuid.uuid4()
    sheet_id = uuid.uuid4()

    mock_exam = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="History Exam",
        exam_date=datetime.now().date(),
        total_marks=100,
        passing_marks=40,
        created_by=uuid.uuid4()
    )

    mock_student = StudentModel(
        id=student_id,
        student_number="S909",
        full_name="Alice Wonderland",
        email="alice@wonderland.com"
    )

    mock_sheet = AnswerSheetModel(
        id=sheet_id,
        exam_id=exam_id,
        student_id=student_id,
        uploaded_by=uuid.uuid4(),
        original_filename="a.pdf",
        stored_filename="a.pdf",
        file_path="",
        file_size_bytes=100,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.VERIFIED,
        processing_status=AnswerSheetStatus.VERIFIED
    )

    mock_result = FinalResultModel(
        id=uuid.uuid4(),
        answer_sheet_id=sheet_id,
        student_id=student_id,
        exam_id=exam_id,
        total_marks_obtained=85.0,
        total_marks_possible=100,
        percentage=85.0,
        grade="A+",
        pass_fail_status=PassFailStatus.PASS,
        is_published=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    async def mock_get(model_class, entity_id):
        if model_class == ExamModel and entity_id == exam_id:
            return mock_exam
        if model_class == StudentModel and entity_id == student_id:
            return mock_student
        if model_class == AnswerSheetModel and entity_id == sheet_id:
            return mock_sheet
        return None

    mock_db.get = mock_get

    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.side_effect = [
        [mock_sheet],  # sheets
        [mock_result]  # results
    ]
    mock_db.execute.return_value = mock_execute_result

    response = client.get(f"/results/exams/{exam_id}/export/csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert response.headers["content-disposition"] == f"attachment; filename=exam_{exam_id}_results.csv"

    # CSV Parsing and Validation
    reader = csv.reader(io.StringIO(response.text))
    rows = list(reader)

    assert rows[0] == [
        "Student Number",
        "Student Name",
        "Marks Obtained",
        "Total Marks",
        "Percentage",
        "Grade",
        "Pass/Fail Status",
        "Verification Status",
        "Publication Status"
    ]
    assert len(rows) == 2
    assert rows[1] == ["S909", "Alice Wonderland", "85.0", "100", "85.0", "A+", "pass", "VERIFIED", "UNPUBLISHED"]


def test_export_exam_results_csv_forbidden_for_student():
    app.dependency_overrides[get_current_user] = override_student_user
    response = client.get(f"/results/exams/{uuid.uuid4()}/export/csv")
    assert response.status_code == 403


def test_export_exam_results_csv_unauthorized():
    app.dependency_overrides[get_current_user] = override_unauthenticated
    response = client.get(f"/results/exams/{uuid.uuid4()}/export/csv")
    assert response.status_code == 401


# ── GET /results/students/{student_id}/export/csv ─────────────────────────────

def test_export_student_results_csv_success():
    from app.infrastructure.persistence.models.student_model import StudentModel
    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.subject_model import SubjectModel
    from app.infrastructure.persistence.models.final_result_model import FinalResultModel

    student_id = uuid.uuid4()
    exam_id = uuid.uuid4()

    mock_student = StudentModel(
        id=student_id,
        student_number="S909",
        full_name="Alice Wonderland",
        email="alice@wonderland.com",
        class_section="A"
    )

    mock_exam = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="History Exam",
        exam_date=datetime.now().date(),
        total_marks=100,
        passing_marks=40,
        created_by=uuid.uuid4()
    )

    mock_subject = SubjectModel(
        id=mock_exam.subject_id,
        name="Social Studies",
        code="SOC1"
    )

    mock_result = FinalResultModel(
        id=uuid.uuid4(),
        answer_sheet_id=uuid.uuid4(),
        student_id=student_id,
        exam_id=exam_id,
        total_marks_obtained=85.0,
        total_marks_possible=100,
        percentage=85.0,
        grade="A+",
        pass_fail_status=PassFailStatus.PASS,
        is_published=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    async def mock_get(model_class, entity_id):
        if model_class == StudentModel and entity_id == student_id:
            return mock_student
        if model_class == ExamModel and entity_id == exam_id:
            return mock_exam
        if model_class == SubjectModel and entity_id == mock_exam.subject_id:
            return mock_subject
        return None

    mock_db.get = mock_get

    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = [mock_result]
    mock_db.execute.return_value = mock_execute_result

    response = client.get(f"/results/students/{student_id}/export/csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert response.headers["content-disposition"] == f"attachment; filename=student_{student_id}_results.csv"

    # CSV Parsing and Validation
    reader = csv.reader(io.StringIO(response.text))
    rows = list(reader)

    assert rows[0] == [
        "Subject Name",
        "Exam Title",
        "Percentage",
        "Grade",
        "Pass/Fail Status",
        "Publication Status"
    ]
    assert len(rows) == 2
    assert rows[1] == ["Social Studies", "History Exam", "85.0", "A+", "pass", "PUBLISHED"]


def test_export_student_results_csv_forbidden_for_student():
    app.dependency_overrides[get_current_user] = override_student_user
    response = client.get(f"/results/students/{uuid.uuid4()}/export/csv")
    assert response.status_code == 403


def test_export_student_results_csv_unauthorized():
    app.dependency_overrides[get_current_user] = override_unauthenticated
    response = client.get(f"/results/students/{uuid.uuid4()}/export/csv")
    assert response.status_code == 401
