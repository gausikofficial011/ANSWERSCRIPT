"""
tests/integration/test_answer_sheet_api.py — Integration Tests for Answer Sheets API
"""

from __future__ import annotations

import io
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
from app.core.constants import UserRole, AnswerSheetStatus

# Setup a transient FastAPI app for endpoint routing integration tests
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
    model_class = None
    if hasattr(query, "column_descriptions") and len(query.column_descriptions) > 0:
        model_class = query.column_descriptions[0].get("entity")

    entity_id = None
    if hasattr(query, "compile"):
        try:
            params = query.compile().params
            for k, val in params.items():
                if k.startswith("id") and isinstance(val, uuid.UUID):
                    entity_id = val
                    break
        except Exception:
            pass

    if model_class and entity_id:
        model = await mock_db.get(model_class, entity_id)
        result = MagicMock()
        result.scalar_one_or_none.return_value = model
        result.scalars.return_value.first.return_value = model
        result.scalar_one.return_value = 1
        result.scalar.return_value = 1
        result.scalars.return_value.all.return_value = [model] if model else []
        return result

    return mock_db.execute.return_value


async def mock_merge(model, *args, **kwargs):
    if not model:
        return model
    if hasattr(model, "id") and hasattr(model, "__class__"):
        try:
            existing = await mock_db.get(model.__class__, model.id)
            if existing:
                for col in model.__table__.columns:
                    val = getattr(model, col.name, None)
                    if val is not None:
                        setattr(existing, col.name, val)
                return existing
        except Exception:
            pass
    return model


@pytest.fixture(autouse=True)
def reset_mocks():
    mock_db.reset_mock()
    mock_db.execute = AsyncMock(side_effect=mock_execute)
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.get = AsyncMock()
    mock_db.merge = AsyncMock(side_effect=mock_merge)
    mock_user.role = UserRole.TEACHER


def test_upload_answer_sheets_endpoint_success():
    exam_id = uuid.uuid4()
    student_id = uuid.uuid4()
    sheet_id = uuid.uuid4()

    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.student_model import StudentModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel

    exam_orm = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Math Midterm",
        total_marks=100,
        passing_marks=40,
        created_by=mock_user.id
    )

    student_orm = StudentModel(
        id=student_id,
        student_number="STU001",
        full_name="Alice Smith",
        email="alice@example.com"
    )

    sheet_orm = AnswerSheetModel(
        id=sheet_id,
        exam_id=exam_id,
        student_id=student_id,
        uploaded_by=mock_user.id,
        original_filename="STU001.pdf",
        stored_filename="stored.pdf",
        file_path="answer_sheets/stored.pdf",
        file_size_bytes=38,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.UPLOADED,
        processing_status=AnswerSheetStatus.UPLOADED.value,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    # Mock database lookups
    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == ExamModel:
            return exam_orm
        if model_class == StudentModel:
            return student_orm
        if model_class == AnswerSheetModel:
            return sheet_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    # Mock database execute calls in the order the use case makes them:
    # 1. exam_repo.get_by_id → returns exam_orm (scalar_one_or_none)
    # 2. answer_sheet_repo.get_by_hash → returns None (no duplicate)
    # 3. student_repo.get_by_student_number (STU001) → returns student_orm (first)
    # 4. answer_sheet_repo.get_by_student_and_exam → returns None (no prev)
    # 5+ save() reloads → return sheet_orm
    execute_call_count = [0]

    async def upload_mock_execute(query, *args, **kwargs):
        execute_call_count[0] += 1
        n = execute_call_count[0]
        result = MagicMock()
        if n == 1:  # exam get_by_id
            result.scalar_one_or_none.return_value = exam_orm
            result.scalars.return_value.first.return_value = exam_orm
        elif n == 2:  # hash duplicate check
            result.scalar_one_or_none.return_value = None
            result.scalars.return_value.first.return_value = None
        elif n == 3:  # student number lookup
            result.scalar_one_or_none.return_value = student_orm
            result.scalars.return_value.first.return_value = student_orm
        elif n == 4:  # get_by_student_and_exam
            result.scalar_one_or_none.return_value = None
            result.scalars.return_value.first.return_value = None
        else:  # save reloads, count queries etc.
            result.scalar_one_or_none.return_value = sheet_orm
            result.scalar_one.return_value = 1
            result.scalars.return_value.all.return_value = [sheet_orm]
            result.scalars.return_value.first.return_value = sheet_orm
        return result

    mock_db.execute = AsyncMock(side_effect=upload_mock_execute)

    # Mock file data
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF"
    file_payload = [
        ("files", ("STU001.pdf", io.BytesIO(pdf_bytes), "application/pdf"))
    ]

    from unittest.mock import patch

    # Patch Celery dispatch to prevent eager execution in async test context
    with patch("app.tasks.ocr_tasks.process_answer_sheet_ocr.delay"):
        response = client.post(
            "/answer-sheets/upload",
            data={
                "exam_id": str(exam_id)
            },
            files=file_payload
        )

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["original_filename"] == "STU001.pdf"
    assert data[0]["mime_type"] == "application/pdf"
    assert data[0]["status"] in ("UPLOADED", "QUEUED_FOR_OCR")


def test_upload_answer_sheets_endpoint_validation_error():
    # Empty file
    file_payload = [
        ("files", ("STU001.pdf", io.BytesIO(b""), "application/pdf"))
    ]
    response = client.post(
        "/answer-sheets/upload",
        data={"exam_id": str(uuid.uuid4())},
        files=file_payload
    )
    assert response.status_code == 400
    assert "empty file" in response.json()["detail"].lower()


def test_get_answer_sheet_endpoint_success():
    sheet_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    
    sheet_orm = AnswerSheetModel(
        id=sheet_id,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=mock_user.id,
        original_filename="math.pdf",
        stored_filename="stored.pdf",
        file_path="answer_sheets/stored.pdf",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.UPLOADED,
        processing_status=AnswerSheetStatus.UPLOADED.value,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == AnswerSheetModel:
            return sheet_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    response = client.get(f"/answer-sheets/{sheet_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sheet_id)
    assert data["original_filename"] == "math.pdf"


def test_delete_answer_sheet_endpoint_success():
    sheet_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    
    sheet_orm = AnswerSheetModel(
        id=sheet_id,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=mock_user.id,
        original_filename="math.pdf",
        stored_filename="stored.pdf",
        file_path="answer_sheets/stored.pdf",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.UPLOADED,
        processing_status=AnswerSheetStatus.UPLOADED.value,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == AnswerSheetModel:
            return sheet_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    # Mock soft delete
    mock_db.flush = AsyncMock()

    response = client.delete(f"/answer-sheets/{sheet_id}")

    assert response.status_code == 200
    assert "deleted successfully" in response.json()["detail"]
