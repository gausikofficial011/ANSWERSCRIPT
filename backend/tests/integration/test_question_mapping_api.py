"""
tests/integration/test_question_mapping_api.py — Integration Tests for Question Mapping APIs
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
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.get = AsyncMock()
    mock_db.merge = AsyncMock(side_effect=mock_merge)
    mock_user.role = UserRole.TEACHER


def test_get_question_mappings_endpoint_success():
    sheet_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.question_mapping_model import QuestionMappingModel
    
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

    mappings_orm = [
        QuestionMappingModel(
            id=uuid.uuid4(),
            answer_sheet_id=sheet_id,
            question_id=uuid.uuid4(),
            detected_question_number=1,
            detected_question_label="Q1",
            extracted_answer_text="Answer text content",
            start_page=1,
            end_page=1,
            mapping_confidence=1.0,
            status="MAPPED",
            duplicate_question_flag=False,
            duplicate_group_id=None,
            source_ocr_result_ids=[uuid.uuid4()],
            source_bounding_boxes=[],
            source_page_numbers=[1],
            answer_word_count=3,
            answer_character_count=19,
            answer_page_count=1,
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
    mock_execute_result.scalars.return_value.all.return_value = mappings_orm
    mock_db.execute.return_value = mock_execute_result

    response = client.get(f"/ocr/{sheet_id}/mappings")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["detected_question_label"] == "Q1"
    assert data[0]["extracted_answer_text"] == "Answer text content"
    assert data[0]["status"] == "MAPPED"


def test_reprocess_question_mappings_endpoint_success():
    sheet_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.ocr_result_model import OCRResultModel
    from app.infrastructure.persistence.models.question_model import QuestionModel
    from app.infrastructure.persistence.models.question_mapping_model import QuestionMappingModel
    
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
            extracted_text="Q1 Answer text content",
            bounding_boxes=[
                {"text": "Q1: ", "confidence": 0.95, "x1": 10, "y1": 20, "x2": 40, "y2": 40},
                {"text": "Answer text content", "confidence": 0.95, "x1": 50, "y1": 20, "x2": 250, "y2": 40}
            ],
            low_confidence_flag=False,
            confidence_score=0.95,
            average_confidence=0.95,
            words_detected=2,
            processing_time=0.4,
            ocr_engine_version="easyocr-1.0",
            preprocessing_version="opencv-1.0",
            original_image_path="",
            processed_image_path="",
            status="OCR_COMPLETED"
        )
    ]

    db_questions = [
        QuestionModel(
            id=uuid.uuid4(),
            exam_id=sheet_orm.exam_id,
            question_number=1,
            question_text="What is Q1?",
            marks=10,
            question_type="short"
        )
    ]

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == AnswerSheetModel:
            return sheet_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    async def reprocess_mock_execute(query, *args, **kwargs):
        query_str = str(query) if query is not None else ""
        result = MagicMock()
        result.rowcount = 1
        
        if "SELECT" in query_str.upper():
            if "answer_sheets" in query_str:
                result.scalar_one_or_none.return_value = sheet_orm
                result.scalars.return_value.first.return_value = sheet_orm
                result.scalars.return_value.all.return_value = [sheet_orm]
            elif "ocr_results" in query_str:
                result.scalars.return_value.all.return_value = ocr_results_orm
            elif "questions" in query_str:
                result.scalars.return_value.all.return_value = db_questions
            else:
                result.scalar_one_or_none.return_value = None
                result.scalars.return_value.all.return_value = []
        return result

    mock_db.execute = AsyncMock(side_effect=reprocess_mock_execute)

    # Mock mapping repo save
    mock_db.merge = AsyncMock(side_effect=mock_merge)

    response = client.post(f"/ocr/{sheet_id}/mappings/reprocess")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["detected_question_label"] == "Q1"
    assert data[0]["extracted_answer_text"] == "Answer text content"
    assert data[0]["status"] == "MAPPED"


def test_get_question_mapping_summary_endpoint_success():
    sheet_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.question_model import QuestionModel
    from app.infrastructure.persistence.models.question_mapping_model import QuestionMappingModel
    
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

    db_questions = [
        QuestionModel(id=uuid.uuid4(), exam_id=sheet_orm.exam_id, question_number=1, question_text="What is Q1?", marks=10, question_type="short"),
        QuestionModel(id=uuid.uuid4(), exam_id=sheet_orm.exam_id, question_number=2, question_text="What is Q2?", marks=10, question_type="short")
    ]

    mappings_orm = [
        QuestionMappingModel(
            id=uuid.uuid4(),
            answer_sheet_id=sheet_id,
            question_id=db_questions[0].id,
            detected_question_number=1,
            status="MAPPED",
            duplicate_question_flag=False,
            source_ocr_result_ids=[],
            source_bounding_boxes=[],
            source_page_numbers=[],
            answer_word_count=0,
            answer_character_count=0,
            answer_page_count=0
        ),
        QuestionMappingModel(
            id=uuid.uuid4(),
            answer_sheet_id=sheet_id,
            question_id=db_questions[1].id,
            detected_question_number=2,
            status="NOT_ATTEMPTED",
            duplicate_question_flag=False,
            source_ocr_result_ids=[],
            source_bounding_boxes=[],
            source_page_numbers=[],
            answer_word_count=0,
            answer_character_count=0,
            answer_page_count=0
        )
    ]

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == AnswerSheetModel:
            return sheet_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    # execute ordering: get_by_id (deleted_at), questions list, mappings list
    summary_call_count = [0]

    async def summary_mock_execute(query, *args, **kwargs):
        summary_call_count[0] += 1
        n = summary_call_count[0]
        result = MagicMock()
        if n == 1:  # answer_sheet_repo.get_by_id
            result.scalar_one_or_none.return_value = sheet_orm
        elif n == 2:  # get questions for exam
            result.scalars.return_value.all.return_value = db_questions
        elif n == 3:  # list mappings by answer_sheet_id
            result.scalars.return_value.all.return_value = mappings_orm
        else:
            result.scalar_one_or_none.return_value = sheet_orm
            result.scalars.return_value.all.return_value = []
        return result

    mock_db.execute = AsyncMock(side_effect=summary_mock_execute)

    response = client.get(f"/ocr/{sheet_id}/mapping-summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_questions"] == 2
    assert data["mapped_questions"] == 1
    assert data["not_attempted_questions"] == 1
    assert data["duplicate_questions"] == 0
    assert data["unmapped_questions"] == 0
