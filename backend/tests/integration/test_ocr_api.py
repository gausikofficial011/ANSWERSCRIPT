"""
tests/integration/test_ocr_api.py — Integration Tests for OCR API
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
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
    mock_db.execute.return_value = MagicMock()
    mock_db.execute.return_value.rowcount = 1
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.get = AsyncMock()
    mock_db.merge = AsyncMock(side_effect=mock_merge)
    mock_user.role = UserRole.TEACHER


def test_get_ocr_results_endpoint_success():
    sheet_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.ocr_result_model import OCRResultModel
    
    sheet_orm = AnswerSheetModel(
        id=sheet_id,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=mock_user.id,
        original_filename="student1.pdf",
        stored_filename="stored.pdf",
        file_path="uploads/stored.pdf",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.OCR_COMPLETED,
        processing_status=AnswerSheetStatus.OCR_COMPLETED.value,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    ocr_results_orm = [
        OCRResultModel(
            id=uuid.uuid4(),
            answer_sheet_id=sheet_id,
            page_number=1,
            extracted_text="page 1 content",
            bounding_boxes=[{"text": "page", "confidence": 0.9, "x1": 0, "y1": 0, "x2": 10, "y2": 10, "page_number": 1, "low_confidence_flag": False}],
            low_confidence_flag=False,
            confidence_score=0.9,
            average_confidence=0.9,
            words_detected=1,
            processing_time=0.4,
            ocr_engine_version="easyocr-1.0",
            preprocessing_version="opencv-1.0",
            original_image_path="uploads/original_images/sheet_1.png",
            processed_image_path="uploads/processed_images/sheet_1.png",
            status="OCR_COMPLETED",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    ]

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == AnswerSheetModel:
            return sheet_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = ocr_results_orm
    mock_db.execute.return_value = mock_execute_result

    response = client.get(f"/ocr/{sheet_id}/results")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["page_number"] == 1
    assert data[0]["extracted_text"] == "page 1 content"
    assert data[0]["bounding_boxes"][0]["text"] == "page"


def test_get_ocr_results_endpoint_not_found():
    sheet_id = uuid.uuid4()
    mock_db.get = AsyncMock(return_value=None)

    response = client.get(f"/ocr/{sheet_id}/results")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_reprocess_ocr_endpoint_success():
    sheet_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    
    sheet_orm = AnswerSheetModel(
        id=sheet_id,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=mock_user.id,
        original_filename="student1.pdf",
        stored_filename="stored.pdf",
        file_path="uploads/stored.pdf",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.FAILED,
        processing_status=AnswerSheetStatus.FAILED.value,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == AnswerSheetModel:
            return sheet_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    with patch("shutil.rmtree") as mock_rmtree, \
         patch("app.tasks.ocr_tasks.process_answer_sheet_ocr.delay") as mock_delay:
        
        response = client.post(f"/ocr/{sheet_id}/reprocess")

        assert response.status_code == 202
        data = response.json()
        assert data["id"] == str(sheet_id)
        assert data["status"] == "QUEUED_FOR_OCR"
        mock_delay.assert_called_once_with(str(sheet_id), force_reprocess=True)
