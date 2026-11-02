"""
tests/integration/test_results_api.py — Integration Tests for Results REST API Endpoints
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router
from app.api.v1.dependencies.auth import get_current_user
from app.infrastructure.persistence.database import get_db_session
from app.domain.entities.user import User
from app.core.constants import UserRole, PassFailStatus, AnswerSheetStatus

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


async def override_current_user():
    return mock_user


app.dependency_overrides[get_db_session] = get_mock_db
app.dependency_overrides[get_current_user] = override_current_user
client = TestClient(app)


async def mock_execute(query, *args, **kwargs):
    import uuid
    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.student_model import StudentModel
    from app.infrastructure.persistence.models.subject_model import SubjectModel
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
def reset_mocks():
    mock_db.reset_mock()
    mock_db.execute = AsyncMock(side_effect=mock_execute)
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.get = AsyncMock()
    mock_db.merge = AsyncMock()
    mock_user.role = UserRole.TEACHER


# ── GET /results/dashboard ────────────────────────────────────────────────────

def test_get_results_dashboard_endpoint_success():
    # Return count values for the dashboard queries
    mock_execute_result = MagicMock()
    mock_execute_result.scalar.side_effect = [10, 6, 75.0, 8]
    mock_db.execute.return_value = mock_execute_result

    response = client.get("/results/dashboard")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["total_students_evaluated"] == 10
    assert json_data["total_published"] == 6
    assert json_data["average_score"] == 75.0
    assert json_data["pass_rate"] == 80.0


# ── GET /results/exams/{exam_id} ──────────────────────────────────────────────

def test_get_exam_results_endpoint_success():
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

    # Mock execute results sequentially:
    # 1. AnswerSheetRepository.get_all_by_exam_id
    # 2. FinalResultRepository.get_by_answer_sheet_id (existing check)
    # 3. FinalResultRepository.get_by_exam_id
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.side_effect = [
        [mock_sheet],  # sheets
        [mock_result]  # results
    ]
    mock_db.execute.return_value = mock_execute_result

    response = client.get(f"/results/exams/{exam_id}")
    print("GET EXAM RESULTS RESPONSE:", response.status_code, response.text)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["exam_title"] == "History Exam"
    assert json_data["total_items"] == 1
    assert json_data["items"][0]["student_name"] == "Alice Wonderland"
    assert json_data["items"][0]["percentage"] == 85.0


# ── GET /results/students/{student_id} ────────────────────────────────────────

def test_get_student_results_endpoint_success():
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

    response = client.get(f"/results/students/{student_id}")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["student_name"] == "Alice Wonderland"
    assert len(json_data["history"]) == 1
    assert json_data["history"][0]["exam_title"] == "History Exam"
    assert json_data["history"][0]["published_status"] == "PUBLISHED"


# ── POST /results/exams/{exam_id}/publish ─────────────────────────────────────

def test_publish_exam_results_endpoint_success():
    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.final_result_model import FinalResultModel

    exam_id = uuid.uuid4()
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

    mock_sheet = AnswerSheetModel(
        id=sheet_id,
        exam_id=exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="a.pdf",
        stored_filename="a.pdf",
        file_path="",
        file_size_bytes=100,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.VERIFIED,
        plagiarism_flagged=False
    )

    mock_result = FinalResultModel(
        id=uuid.uuid4(),
        answer_sheet_id=sheet_id,
        student_id=mock_sheet.student_id,
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
        if model_class == AnswerSheetModel and entity_id == sheet_id:
            return mock_sheet
        return None

    mock_db.get = mock_get

    # Sequential query returns:
    # 1. get_all_by_exam_id (sheets)
    # 2. get_by_exam_id (results)
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.side_effect = [
        [mock_sheet],  # sheets
        [mock_result]  # results
    ]
    # Update rowcount for publish query
    mock_execute_result.rowcount = 1
    mock_db.execute.return_value = mock_execute_result

    response = client.post(f"/results/exams/{exam_id}/publish")
    print("PUBLISH RESPONSE:", response.status_code, response.text)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["published_count"] == 1
    assert json_data["exam_id"] == str(exam_id)


def test_publish_exam_results_forbidden_for_student():
    mock_user.role = "student" # Set non-teacher role

    response = client.post(f"/results/exams/{uuid.uuid4()}/publish")

    assert response.status_code == 403


def test_publish_exam_results_validation_failure_unverified():
    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel

    exam_id = uuid.uuid4()

    mock_exam = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="History Exam",
        exam_date=datetime.now().date(),
        total_marks=100,
        passing_marks=40,
        created_by=uuid.uuid4()
    )

    mock_sheet = AnswerSheetModel(
        id=uuid.uuid4(),
        exam_id=exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="a.pdf",
        stored_filename="a.pdf",
        file_path="",
        file_size_bytes=100,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.EVALUATION_COMPLETED, # Unverified sheet!
        plagiarism_flagged=False
    )

    async def mock_get(model_class, entity_id):
        if model_class == ExamModel and entity_id == exam_id:
            return mock_exam
        return None

    mock_db.get = mock_get

    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = [mock_sheet]
    mock_db.execute.return_value = mock_execute_result

    response = client.post(f"/results/exams/{exam_id}/publish")

    assert response.status_code == 400
    assert "incomplete verification" in response.json()["detail"]
