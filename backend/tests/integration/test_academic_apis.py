"""
tests/integration/test_academic_apis.py — Integration Tests for Academic API Endpoints
"""

from __future__ import annotations

import uuid
from datetime import datetime, date, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router
from app.api.v1.dependencies.auth import get_current_user
from app.infrastructure.persistence.database import get_db_session
from app.domain.entities.user import User
from app.core.constants import UserRole, GradingMode, ExamStatus, QuestionType

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
    # Reset role to Teacher by default
    mock_user.role = UserRole.TEACHER


def test_create_subject_success():
    subject_id = uuid.uuid4()
    
    # Mock repositories inside use case
    from app.infrastructure.persistence.models.subject_model import SubjectModel
    from app.infrastructure.persistence.models.audit_log_model import AuditLogModel
    
    subject_orm = SubjectModel(
        id=subject_id,
        name="Mathematics",
        code="MATH101",
        description="Intro to math",
        language="en",
        is_active=True,
        created_by=mock_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    # get_by_code returns None (no duplicate)
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.first.return_value = None
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_execute_result

    # Mock get reloads
    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == SubjectModel:
            return subject_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    response = client.post(
        "/subjects",
        json={
            "name": "Mathematics",
            "code": "MATH101",
            "description": "Intro to math",
            "language": "en"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Mathematics"
    assert data["code"] == "MATH101"
    assert "id" in data


def test_create_subject_insufficient_role():
    # Set mock user role to Student or non-privileged (wait, UserRole only has admin, teacher in this application)
    # Let's mock UserRole.TEACHER role check failure by raising an Exception or changing role
    mock_user.role = "student"  # invalid role for require_teacher guard

    response = client.post(
        "/subjects",
        json={
            "name": "Mathematics",
            "code": "MATH101",
            "description": "Intro to math",
            "language": "en"
        }
    )

    assert response.status_code == 403
    assert "require" in response.json()["detail"].lower()


def test_create_exam_success():
    exam_id = uuid.uuid4()
    subject_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.subject_model import SubjectModel
    
    subject_orm = SubjectModel(
        id=subject_id,
        name="Physics",
        code="PHYS101",
        description="Intro to physics",
        language="en",
        is_active=True,
        created_by=mock_user.id
    )

    exam_orm = ExamModel(
        id=exam_id,
        subject_id=subject_id,
        title="Midterm",
        description="Physics Midterm",
        exam_date=date.today(),
        total_marks=100,
        passing_marks=40,
        duration_minutes=120,
        status=ExamStatus.DRAFT,
        scoring_config={},
        created_by=mock_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == SubjectModel:
            return subject_orm
        if model_class == ExamModel:
            return exam_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    response = client.post(
        "/exams",
        json={
            "subject_id": str(subject_id),
            "title": "Midterm",
            "description": "Physics Midterm",
            "exam_date": str(date.today()),
            "total_marks": 100,
            "passing_marks": 40,
            "duration_minutes": 120,
            "status": "draft",
            "scoring_config": {}
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Midterm"
    assert data["total_marks"] == 100
    assert data["passing_marks"] == 40


def test_create_exam_invalid_marks():
    response = client.post(
        "/exams",
        json={
            "subject_id": str(uuid.uuid4()),
            "title": "Midterm",
            "exam_date": str(date.today()),
            "total_marks": 50,
            "passing_marks": 60,  # passing > total -> invalid
            "status": "draft"
        }
    )
    assert response.status_code == 422  # validation error in Pydantic schema


def test_get_exam_success():
    exam_id = uuid.uuid4()
    subject_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.exam_model import ExamModel
    
    exam_orm = ExamModel(
        id=exam_id,
        subject_id=subject_id,
        title="Midterm",
        description="Physics Midterm",
        exam_date=date.today(),
        total_marks=100,
        passing_marks=40,
        duration_minutes=120,
        status=ExamStatus.DRAFT,
        scoring_config={},
        created_by=mock_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == ExamModel and entity_id == exam_id:
            return exam_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    response = client.get(f"/exams/{exam_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(exam_id)
    assert data["title"] == "Midterm"


def test_get_exam_not_found():
    mock_db.get = AsyncMock(return_value=None)
    response = client.get(f"/exams/{uuid.uuid4()}")
    assert response.status_code == 404


def test_update_exam_success():
    exam_id = uuid.uuid4()
    subject_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.exam_model import ExamModel
    
    exam_orm = ExamModel(
        id=exam_id,
        subject_id=subject_id,
        title="Original Title",
        description="Original Description",
        exam_date=date.today(),
        total_marks=100,
        passing_marks=40,
        duration_minutes=120,
        status=ExamStatus.DRAFT,
        scoring_config={},
        created_by=mock_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == ExamModel and entity_id == exam_id:
            return exam_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    response = client.put(
        f"/exams/{exam_id}",
        json={
            "title": "Updated Title",
            "total_marks": 80,
            "passing_marks": 35
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["total_marks"] == 80
    assert data["passing_marks"] == 35


def test_update_exam_not_found():
    mock_db.get = AsyncMock(return_value=None)
    response = client.put(
        f"/exams/{uuid.uuid4()}",
        json={
            "title": "Updated Title",
            "total_marks": 80,
            "passing_marks": 35
        }
    )
    assert response.status_code == 404


def test_update_exam_invalid_marks():
    response = client.put(
        f"/exams/{uuid.uuid4()}",
        json={
            "title": "Updated Title",
            "total_marks": 50,
            "passing_marks": 60  # invalid
        }
    )
    assert response.status_code == 422  # validation error in Pydantic schema


def test_delete_exam_success():
    exam_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.exam_model import ExamModel
    
    exam_orm = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Delete Me",
        exam_date=date.today(),
        total_marks=100,
        passing_marks=40,
        duration_minutes=120,
        status=ExamStatus.DRAFT,
        scoring_config={},
        created_by=mock_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == ExamModel and entity_id == exam_id:
            return exam_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    response = client.delete(f"/exams/{exam_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Exam deleted successfully."


def test_delete_exam_not_found():
    mock_db.get = AsyncMock(return_value=None)
    response = client.delete(f"/exams/{uuid.uuid4()}")
    assert response.status_code == 404


def test_list_exams_success():
    exam_id = uuid.uuid4()
    subject_id = uuid.uuid4()
    
    from app.infrastructure.persistence.models.exam_model import ExamModel
    
    exam_orm = ExamModel(
        id=exam_id,
        subject_id=subject_id,
        title="Final Exam",
        description="Math final",
        exam_date=date.today(),
        total_marks=100,
        passing_marks=40,
        duration_minutes=120,
        status=ExamStatus.DRAFT,
        scoring_config={},
        created_by=mock_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    # Mock execute for count and select queries
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    
    data_result = MagicMock()
    data_result.scalars.return_value.all.return_value = [exam_orm]

    mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

    response = client.get("/exams", params={"page": 1, "page_size": 10, "search": "Final", "subject_id": str(subject_id), "status": "draft"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Final Exam"


def test_create_question_success():
    question_id = uuid.uuid4()
    exam_id = uuid.uuid4()

    from app.infrastructure.persistence.models.question_model import QuestionModel
    from app.infrastructure.persistence.models.exam_model import ExamModel

    exam_orm = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Physics",
        total_marks=100,
        passing_marks=40,
        created_by=mock_user.id
    )

    question_orm = QuestionModel(
        id=question_id,
        exam_id=exam_id,
        question_number=1,
        question_text="What is gravity?",
        marks=10,
        question_type=QuestionType.SHORT,
        language="en",
        created_by=mock_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == ExamModel:
            return exam_orm
        if model_class == QuestionModel:
            return question_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.first.return_value = None
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_execute_result

    response = client.post(
        "/questions",
        json={
            "exam_id": str(exam_id),
            "question_number": 1,
            "question_text": "What is gravity?",
            "marks": 10,
            "question_type": "short",
            "language": "en"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["question_number"] == 1
    assert data["marks"] == 10


def test_create_rubric_success():
    rubric_id = uuid.uuid4()
    question_id = uuid.uuid4()

    from app.infrastructure.persistence.models.rubric_model import RubricModel
    from app.infrastructure.persistence.models.question_model import QuestionModel
    from app.infrastructure.persistence.models.rubric_criterion_model import RubricCriterionModel

    question_orm = QuestionModel(
        id=question_id,
        exam_id=uuid.uuid4(),
        question_number=1,
        question_text="Describe photosynthesis.",
        marks=10,
        created_by=mock_user.id
    )

    rubric_orm = RubricModel(
        id=rubric_id,
        question_id=question_id,
        title="Grading details",
        total_weight=1.0,
        version=1,
        is_active=True,
        grading_mode=GradingMode.AI,
        created_by=mock_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        criteria=[]
    )

    async def mock_get(model_class, entity_id, *args, **kwargs):
        if model_class == QuestionModel:
            return question_orm
        if model_class == RubricModel:
            return rubric_orm
        return None
    mock_db.get = AsyncMock(side_effect=mock_get)

    # Mock criterion save batch returns list of criterion orm models
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_execute_result

    response = client.post(
        "/rubrics",
        json={
            "question_id": str(question_id),
            "title": "Grading details",
            "total_weight": 1.0,
            "grading_mode": "ai",
            "criteria": [
                {
                    "criterion_name": "Accuracy",
                    "weight": 0.7,
                    "max_marks": 7.0,
                    "expected_keywords": ["sunlight", "chlorophyll"],
                    "order_index": 0
                },
                {
                    "criterion_name": "Grammar",
                    "weight": 0.3,
                    "max_marks": 3.0,
                    "expected_keywords": [],
                    "order_index": 1
                }
            ]
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Grading details"
    assert data["total_weight"] == 1.0
