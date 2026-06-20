"""
tests/integration/test_evaluations_api.py — Integration Tests for Evaluations API
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
from app.core.constants import UserRole

# Setup transient FastAPI app
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


def test_get_evaluation_endpoint_success():
    eval_id = uuid.uuid4()
    
    # Mock database retrieval logic
    from app.infrastructure.persistence.models.evaluation_model import EvaluationModel
    from app.infrastructure.persistence.models.criterion_evaluation_model import CriterionEvaluationModel
    from app.infrastructure.persistence.models.evaluation_revision_model import EvaluationRevisionModel
    
    mock_eval_model = EvaluationModel(
        id=eval_id,
        answer_sheet_id=uuid.uuid4(),
        question_mapping_id=uuid.uuid4(),
        question_id=uuid.uuid4(),
        model_answer_id=uuid.uuid4(),
        rubric_id=uuid.uuid4(),
        max_marks=10,
        ai_score=6.0,
        similarity_score=0.6,
        keyword_match_score=0.6,
        ai_feedback="Good",
        teacher_score=None,
        teacher_feedback=None,
        final_score=6.0,
        is_verified=False,
        evaluation_confidence=0.8,
        explanation={
            "strengths": "Good explanation.",
            "weaknesses": "Slight spelling errors.",
            "missing_topics": [],
            "improvement_suggestions": "Try focusing on spelling.",
            "scoring_reasoning": "Standard weights."
        },
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Setup AsyncMock database session returns
    async def mock_get(model_class, entity_id):
        if model_class == EvaluationModel and entity_id == eval_id:
            return mock_eval_model
        return None
        
    mock_db.get = mock_get
    
    # Mock list executions for criteria and revisions
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_execute_result

    response = client.get(f"/evaluations/{eval_id}")
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["evaluation"]["id"] == str(eval_id)
    assert json_data["evaluation"]["ai_score"] == 6.0
    assert json_data["evaluation"]["is_verified"] is False
    assert json_data["evaluation"]["explanation"]["strengths"] == "Good explanation."


def test_verify_evaluation_endpoint_success():
    eval_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.evaluation_model import EvaluationModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    
    mock_eval_model = EvaluationModel(
        id=eval_id,
        answer_sheet_id=uuid.uuid4(),
        question_mapping_id=uuid.uuid4(),
        question_id=uuid.uuid4(),
        model_answer_id=uuid.uuid4(),
        rubric_id=uuid.uuid4(),
        max_marks=10,
        ai_score=4.0,
        similarity_score=0.4,
        keyword_match_score=0.4,
        ai_feedback="Mediocre",
        teacher_score=None,
        teacher_feedback=None,
        final_score=4.0,
        is_verified=False,
        evaluation_confidence=0.5,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    mock_sheet_model = AnswerSheetModel(
        id=mock_eval_model.answer_sheet_id,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="ans.pdf",
        stored_filename="ans_stored.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        status="EVALUATION_COMPLETED",
        processing_status="EVALUATION_COMPLETED",
        file_hash="hash"
    )
    
    async def mock_get(model_class, entity_id):
        if model_class == EvaluationModel and entity_id == eval_id:
            return mock_eval_model
        if model_class == AnswerSheetModel and entity_id == mock_eval_model.answer_sheet_id:
            return mock_sheet_model
        return None
        
    mock_db.get = mock_get
    
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = [mock_eval_model]
    mock_db.execute.return_value = mock_execute_result

    payload = {
        "teacher_score": 8.0,
        "teacher_feedback": "Excellent correction in person.",
        "reason": "Clarified formula error",
        "criterion_overrides": []
    }
    
    response = client.post(f"/evaluations/{eval_id}/verify", json=payload)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["is_verified"] is True
    assert json_data["teacher_score"] == 8.0
    assert json_data["teacher_feedback"] == "Excellent correction in person."


def test_get_explanation_endpoint_success():
    eval_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.evaluation_model import EvaluationModel
    
    mock_eval_model = EvaluationModel(
        id=eval_id,
        answer_sheet_id=uuid.uuid4(),
        question_mapping_id=uuid.uuid4(),
        question_id=uuid.uuid4(),
        model_answer_id=uuid.uuid4(),
        rubric_id=uuid.uuid4(),
        max_marks=10,
        ai_score=8.0,
        explanation={
            "strengths": "Strong core logic.",
            "weaknesses": "Lacks references.",
            "missing_topics": ["references"],
            "improvement_suggestions": "Read more journals.",
            "scoring_reasoning": "Standard weights."
        },
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    async def mock_get(model_class, entity_id):
        if model_class == EvaluationModel and entity_id == eval_id:
            return mock_eval_model
        return None
        
    mock_db.get = mock_get

    response = client.get(f"/evaluations/{eval_id}/explanation")
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["strengths"] == "Strong core logic."
    assert json_data["missing_topics"] == ["references"]
