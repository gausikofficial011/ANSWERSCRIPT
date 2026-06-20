"""
tests/integration/test_plagiarism_api.py — Integration Tests for Plagiarism API
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
from app.core.constants import UserRole, PlagiarismStatus

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


@pytest.fixture(autouse=True)
def reset_mocks():
    mock_db.reset_mock()
    mock_db.execute = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.get = AsyncMock()
    mock_db.merge = AsyncMock()
    mock_user.role = UserRole.TEACHER


def test_list_plagiarism_reports_success():
    from app.infrastructure.persistence.models.plagiarism_report_model import PlagiarismReportModel

    report_id = uuid.uuid4()
    mock_report = PlagiarismReportModel(
        id=report_id,
        exam_id=uuid.uuid4(),
        source_answer_sheet_id=uuid.uuid4(),
        target_answer_sheet_id=uuid.uuid4(),
        similarity_percentage=85.0,
        highest_similarity=0.85,
        risk_level="HIGH_RISK",
        status=PlagiarismStatus.DETECTED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = [mock_report]
    mock_db.execute.return_value = mock_execute_result

    response = client.get("/plagiarism/reports")

    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data) == 1
    assert json_data[0]["id"] == str(report_id)
    assert json_data[0]["highest_similarity"] == 0.85
    assert json_data[0]["risk_level"] == "HIGH_RISK"


def test_get_answer_sheet_reports_success():
    from app.infrastructure.persistence.models.plagiarism_report_model import PlagiarismReportModel

    sheet_id = uuid.uuid4()
    report_id = uuid.uuid4()
    mock_report = PlagiarismReportModel(
        id=report_id,
        exam_id=uuid.uuid4(),
        source_answer_sheet_id=sheet_id,
        target_answer_sheet_id=uuid.uuid4(),
        similarity_percentage=75.0,
        highest_similarity=0.75,
        risk_level="SUSPICIOUS",
        status=PlagiarismStatus.DETECTED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = [mock_report]
    mock_db.execute.return_value = mock_execute_result

    response = client.get(f"/plagiarism/{sheet_id}")

    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data) == 1
    assert json_data[0]["id"] == str(report_id)
    assert json_data[0]["source_answer_sheet_id"] == str(sheet_id)


def test_get_report_similarities_success():
    from app.infrastructure.persistence.models.plagiarism_report_model import PlagiarismReportModel
    from app.infrastructure.persistence.models.plagiarism_similarity_model import PlagiarismSimilarityModel

    report_id = uuid.uuid4()
    sheet_id1 = uuid.uuid4()
    sheet_id2 = uuid.uuid4()

    mock_report = PlagiarismReportModel(
        id=report_id,
        exam_id=uuid.uuid4(),
        source_answer_sheet_id=sheet_id1,
        target_answer_sheet_id=sheet_id2,
        similarity_percentage=85.0,
        highest_similarity=0.85,
        risk_level="HIGH_RISK",
        status=PlagiarismStatus.DETECTED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_similarity = PlagiarismSimilarityModel(
        id=uuid.uuid4(),
        source_answer_sheet_id=sheet_id1,
        target_answer_sheet_id=sheet_id2,
        source_question_mapping_id=uuid.uuid4(),
        target_question_mapping_id=uuid.uuid4(),
        semantic_similarity=0.9,
        lexical_similarity=0.8,
        overlap_similarity=0.8,
        final_similarity=0.85,
        risk_level="HIGH_RISK",
        created_at=datetime.now(timezone.utc)
    )

    async def mock_get(model_class, entity_id):
        if model_class == PlagiarismReportModel and entity_id == report_id:
            return mock_report
        return None

    mock_db.get = mock_get

    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = [mock_similarity]
    mock_db.execute.return_value = mock_execute_result

    response = client.get(f"/plagiarism/{report_id}/similarities")

    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data) == 1
    assert json_data[0]["final_similarity"] == 0.85


def test_review_plagiarism_report_success():
    from app.infrastructure.persistence.models.plagiarism_report_model import PlagiarismReportModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel

    report_id = uuid.uuid4()
    sheet_id1 = uuid.uuid4()
    sheet_id2 = uuid.uuid4()

    mock_report = PlagiarismReportModel(
        id=report_id,
        exam_id=uuid.uuid4(),
        source_answer_sheet_id=sheet_id1,
        target_answer_sheet_id=sheet_id2,
        similarity_percentage=85.0,
        highest_similarity=0.85,
        risk_level="HIGH_RISK",
        status=PlagiarismStatus.DETECTED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_sheet1 = AnswerSheetModel(
        id=sheet_id1,
        exam_id=mock_report.exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="s1.pdf",
        stored_filename="s1.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        status="PLAGIARISM_REVIEW_PENDING",
        processing_status="EVALUATION_COMPLETED",
        file_hash="hash1",
        plagiarism_flagged=True
    )
    mock_sheet2 = AnswerSheetModel(
        id=sheet_id2,
        exam_id=mock_report.exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="s2.pdf",
        stored_filename="s2.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        status="PLAGIARISM_REVIEW_PENDING",
        processing_status="EVALUATION_COMPLETED",
        file_hash="hash2",
        plagiarism_flagged=True
    )

    async def mock_get(model_class, entity_id):
        if model_class == PlagiarismReportModel and entity_id == report_id:
            return mock_report
        if model_class == AnswerSheetModel and entity_id == sheet_id1:
            return mock_sheet1
        if model_class == AnswerSheetModel and entity_id == sheet_id2:
            return mock_sheet2
        return None

    mock_db.get = mock_get

    async def mock_execute(query):
        q_str = str(query)
        mock_res = MagicMock()
        if "answer_sheets" in q_str:
            if str(sheet_id1) in q_str:
                mock_res.scalar_one_or_none.return_value = mock_sheet1
                mock_res.scalars.return_value.all.return_value = [mock_sheet1]
            elif str(sheet_id2) in q_str:
                mock_res.scalar_one_or_none.return_value = mock_sheet2
                mock_res.scalars.return_value.all.return_value = [mock_sheet2]
            else:
                mock_res.scalar_one_or_none.return_value = mock_sheet1
                mock_res.scalars.return_value.all.return_value = [mock_sheet1]
        else:
            mock_res.scalar_one_or_none.return_value = None
            mock_res.scalars.return_value.all.return_value = []
        return mock_res

    mock_db.execute = mock_execute

    async def mock_merge(model_instance):
        if model_instance.id == report_id:
            mock_report.status = model_instance.status
            mock_report.teacher_notes = model_instance.teacher_notes
            mock_report.reviewed_by = model_instance.reviewed_by
            mock_report.reviewed_at = model_instance.reviewed_at
            mock_report.updated_at = model_instance.updated_at
        elif model_instance.id == sheet_id1:
            mock_sheet1.plagiarism_flagged = model_instance.plagiarism_flagged
            mock_sheet1.status = model_instance.status
        elif model_instance.id == sheet_id2:
            mock_sheet2.plagiarism_flagged = model_instance.plagiarism_flagged
            mock_sheet2.status = model_instance.status
        return model_instance

    mock_db.merge = mock_merge

    payload = {
        "status": "FALSE_POSITIVE",
        "teacher_notes": "Not plagiarism."
    }

    response = client.post(f"/plagiarism/{report_id}/review", json=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "FALSE_POSITIVE"
    assert mock_report.status == PlagiarismStatus.FALSE_POSITIVE
    assert mock_sheet1.plagiarism_flagged is False
    assert mock_sheet1.status == "EVALUATION_COMPLETED"


def test_get_exam_plagiarism_summary_success():
    from app.infrastructure.persistence.models.plagiarism_report_model import PlagiarismReportModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel

    exam_id = uuid.uuid4()
    sheet_id1 = uuid.uuid4()
    sheet_id2 = uuid.uuid4()
    report_id = uuid.uuid4()

    mock_report = PlagiarismReportModel(
        id=report_id,
        exam_id=exam_id,
        source_answer_sheet_id=sheet_id1,
        target_answer_sheet_id=sheet_id2,
        similarity_percentage=85.0,
        highest_similarity=0.85,
        risk_level="HIGH_RISK",
        status=PlagiarismStatus.DETECTED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_sheet1 = AnswerSheetModel(
        id=sheet_id1,
        exam_id=exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="s1.pdf",
        stored_filename="s1.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        status="PLAGIARISM_REVIEW_PENDING",
        processing_status="EVALUATION_COMPLETED",
        file_hash="hash1",
        plagiarism_flagged=True
    )

    mock_exec_result_reports = MagicMock()
    mock_exec_result_reports.scalars.return_value.all.return_value = [mock_report]

    mock_exec_result_sheets = MagicMock()
    mock_exec_result_sheets.scalars.return_value.all.return_value = [mock_sheet1]

    mock_db.execute.side_effect = [mock_exec_result_reports, mock_exec_result_sheets]

    response = client.get(f"/plagiarism/exams/{exam_id}/summary")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["exam_id"] == str(exam_id)
    assert json_data["total_reports"] == 1
    assert json_data["high_risk_count"] == 1
    assert json_data["highest_similarity"] == 0.85
    assert json_data["flagged_sheets_count"] == 1
