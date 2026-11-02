"""
tests/integration/test_security_hardening.py — Integration Tests for Security Hardening Gaps (Phase 14B)
"""

from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router
from app.api.v1.dependencies.auth import get_current_user
from app.infrastructure.persistence.database import get_db_session
from app.domain.entities.user import User
from app.core.constants import UserRole, AnswerSheetStatus, PlagiarismStatus, PassFailStatus

# Models
from app.infrastructure.persistence.models.student_model import StudentModel
from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
from app.infrastructure.persistence.models.evaluation_model import EvaluationModel
from app.infrastructure.persistence.models.final_result_model import FinalResultModel
from app.infrastructure.persistence.models.exam_model import ExamModel
from app.infrastructure.persistence.models.subject_model import SubjectModel
from app.infrastructure.persistence.models.plagiarism_report_model import PlagiarismReportModel
from app.infrastructure.persistence.models.plagiarism_similarity_model import PlagiarismSimilarityModel
from app.infrastructure.persistence.models.criterion_evaluation_model import CriterionEvaluationModel
from app.infrastructure.persistence.models.evaluation_revision_model import EvaluationRevisionModel

app = FastAPI()
app.include_router(api_router)

mock_db = MagicMock(spec=AsyncSession)
mock_user = User(
    id=uuid.uuid4(),
    email="student@example.com",
    username="student1",
    hashed_password="hash",
    full_name="Student One",
    role="student",
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

# Global test databases to simulate persistence
students_db = {}
answer_sheets_db = {}
evaluations_db = {}
final_results_db = {}
exams_db = {}
subjects_db = {}
plagiarism_reports_db = {}
criterion_evaluations_db = {}
evaluation_revisions_db = {}

db_map = {
    StudentModel: students_db,
    AnswerSheetModel: answer_sheets_db,
    EvaluationModel: evaluations_db,
    FinalResultModel: final_results_db,
    ExamModel: exams_db,
    SubjectModel: subjects_db,
    PlagiarismReportModel: plagiarism_reports_db,
    CriterionEvaluationModel: criterion_evaluations_db,
    EvaluationRevisionModel: evaluation_revisions_db,
}

def backfill_model(item):
    if item is None:
        return None
    if isinstance(item, AnswerSheetModel):
        if getattr(item, "uploaded_by", None) is None:
            item.uploaded_by = uuid.uuid4()
        if getattr(item, "created_at", None) is None:
            item.created_at = datetime.now(timezone.utc)
        if getattr(item, "updated_at", None) is None:
            item.updated_at = datetime.now(timezone.utc)
    elif isinstance(item, EvaluationModel):
        if getattr(item, "question_mapping_id", None) is None:
            item.question_mapping_id = uuid.uuid4()
        if getattr(item, "model_answer_id", None) is None:
            item.model_answer_id = uuid.uuid4()
        if getattr(item, "max_marks", None) is None:
            item.max_marks = 10
        if getattr(item, "is_verified", None) is None:
            item.is_verified = False
        explanation = getattr(item, "explanation", None) or {}
        if not isinstance(explanation, dict):
            explanation = {}
        if "strengths" not in explanation:
            explanation["strengths"] = "N/A"
        if "weaknesses" not in explanation:
            explanation["weaknesses"] = "N/A"
        if "missing_topics" not in explanation:
            explanation["missing_topics"] = []
        if "improvement_suggestions" not in explanation:
            explanation["improvement_suggestions"] = "N/A"
        if "scoring_reasoning" not in explanation:
            explanation["scoring_reasoning"] = "N/A"
        item.explanation = explanation
        if getattr(item, "created_at", None) is None:
            item.created_at = datetime.now(timezone.utc)
        if getattr(item, "updated_at", None) is None:
            item.updated_at = datetime.now(timezone.utc)
    return item

async def mock_execute(query, *args, **kwargs):
    # 1. Determine model class
    model_class = None
    if hasattr(query, "column_descriptions") and len(query.column_descriptions) > 0:
        model_class = query.column_descriptions[0].get("entity")

    # Fallback to check tablename in compiled query string
    if model_class is None:
        try:
            sql_str = str(query)
            for m in db_map:
                if hasattr(m, "__tablename__") and m.__tablename__ in sql_str:
                    model_class = m
                    break
        except Exception:
            pass

    # 2. Extract params
    params = {}
    if hasattr(query, "compile"):
        try:
            params = query.compile().params
        except Exception:
            pass

    print(f"[MOCK EXECUTE] model_class={model_class}, params={params}")

    if model_class in db_map:
        db = db_map[model_class]
        items = list(db.values())
        
        # Apply filters
        # 1. ID filter: check if query filters by id
        id_param = params.get("id_1") or params.get("id")
        if id_param:
            items = [item for item in items if getattr(item, "id", None) == id_param]
            
        # 2. Student ID filter
        student_id_param = params.get("student_id_1") or params.get("student_id")
        if student_id_param:
            items = [item for item in items if getattr(item, "student_id", None) == student_id_param]
            
        # 3. Exam ID filter
        exam_id_param = params.get("exam_id_1") or params.get("exam_id")
        if exam_id_param:
            items = [item for item in items if getattr(item, "exam_id", None) == exam_id_param]
            
        # 4. Email filter
        email_param = params.get("email_1") or params.get("email") or params.get("lower_1")
        if email_param:
            items = [item for item in items if getattr(item, "email", None) == email_param]
            
        # 5. Answer Sheet ID filter
        answer_sheet_id_param = params.get("answer_sheet_id_1") or params.get("answer_sheet_id")
        if answer_sheet_id_param:
            items = [item for item in items if getattr(item, "answer_sheet_id", None) == answer_sheet_id_param]

        # 6. Source Answer Sheet ID filter (for plagiarism reports)
        source_sheet_id_param = params.get("source_answer_sheet_id_1") or params.get("source_answer_sheet_id")
        if source_sheet_id_param:
            items = [item for item in items if getattr(item, "source_answer_sheet_id", None) == source_sheet_id_param or getattr(item, "target_answer_sheet_id", None) == source_sheet_id_param]

        # 7. Evaluation ID filter (for criterion evaluations)
        evaluation_id_param = params.get("evaluation_id_1") or params.get("evaluation_id")
        if evaluation_id_param:
            items = [item for item in items if getattr(item, "evaluation_id", None) == evaluation_id_param]

        # 8. Student number filter
        student_number_param = params.get("student_number_1") or params.get("student_number")
        if student_number_param:
            items = [item for item in items if getattr(item, "student_number", None) == student_number_param]

        # Fill validation fields for AnswerSheetModel and EvaluationModel
        for item in items:
            backfill_model(item)

        # Create mock result
        res = MagicMock()
        res.scalar.return_value = len(items)
        res.scalar_one.return_value = len(items)
        res.scalar_one_or_none.return_value = items[0] if items else None
        res.scalars.return_value.all.return_value = items
        res.scalars.return_value.first.return_value = items[0] if items else None
        return res

    return mock_db.execute.return_value

async def mock_get(model_class, entity_id, *args, **kwargs):
    print(f"[MOCK GET] model_class={model_class}, entity_id={entity_id}")
    if model_class in db_map:
        item = db_map[model_class].get(entity_id)
        if item is not None:
            backfill_model(item)
        print(f"[MOCK GET RESULT] found={item is not None}")
        return item
    return None

@pytest.fixture(autouse=True)
def setup_test_data():
    mock_db.reset_mock()
    mock_db.execute = AsyncMock(side_effect=mock_execute)
    mock_db.get = AsyncMock(side_effect=mock_get)
    
    # Intercept add/merge calls to persist in-memory
    def mock_add(model):
        model_class = type(model)
        backfill_model(model)
        print(f"[MOCK ADD] model_class={model_class}, id={getattr(model, 'id', None)}, uploaded_by={getattr(model, 'uploaded_by', None)}")
        if model_class in db_map:
            db_map[model_class][model.id] = model

    async def mock_merge(model):
        model_class = type(model)
        backfill_model(model)
        print(f"[MOCK MERGE] model_class={model_class}, id={getattr(model, 'id', None)}, uploaded_by={getattr(model, 'uploaded_by', None)}")
        if model_class in db_map:
            db_map[model_class][model.id] = model
        return model

    mock_db.add = MagicMock(side_effect=mock_add)
    mock_db.flush = AsyncMock()
    mock_db.merge = AsyncMock(side_effect=mock_merge)
    mock_db.commit = AsyncMock()

    # Clear databases
    for db in db_map.values():
        db.clear()

    # Set default role
    mock_user.role = "student"
    mock_user.email = "student@example.com"

    from app.domain.exceptions.file_exceptions import CorruptedFileException
    def mock_verify(self, file_data: bytes, filename: str) -> None:
        ext = filename.split(".")[-1].lower()
        if ext == "pdf":
            if not file_data.startswith(b"%PDF-"):
                raise CorruptedFileException(filename, "Invalid PDF header signature")
        elif ext == "png":
            if not file_data.startswith(b"\x89PNG\r\n\x1a\n"):
                raise CorruptedFileException(filename, "Invalid PNG magic numbers")
        elif ext in ("jpg", "jpeg"):
            if not file_data.startswith(b"\xff\xd8\xff"):
                raise CorruptedFileException(filename, "Invalid JPEG magic numbers")
        else:
            raise CorruptedFileException(filename, "Unsupported file format")

    with patch("app.infrastructure.storage.file_metadata_service.FileMetadataService.verify_integrity", mock_verify):
        yield



# ── OWNERSHIP & AUTHORIZATION TESTS ──────────────────────────────────────────

def test_student_access_own_evaluation():
    student_id = uuid.uuid4()
    sheet_id = uuid.uuid4()
    eval_id = uuid.uuid4()

    mock_user.email = "student@example.com"
    mock_user.role = "student"

    students_db[student_id] = StudentModel(
        id=student_id,
        email="student@example.com",
        student_number="S123",
        full_name="Student One",
        class_section="A"
    )

    answer_sheets_db[sheet_id] = AnswerSheetModel(
        id=sheet_id,
        student_id=student_id,
        exam_id=uuid.uuid4(),
        original_filename="test.pdf",
        stored_filename="stored.pdf",
        file_path="paths",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.VERIFIED
    )

    evaluations_db[eval_id] = EvaluationModel(
        id=eval_id,
        answer_sheet_id=sheet_id,
        question_id=uuid.uuid4(),
        ai_score=8.5,
        final_score=8.5,
        explanation={"strengths": "Good structure", "weaknesses": "Slight typos"}
    )

    # 1. Test GET /evaluations/{id}
    response = client.get(f"/evaluations/{eval_id}")
    assert response.status_code == 200
    assert response.json()["evaluation"]["id"] == str(eval_id)

    # 2. Test GET /evaluations/{id}/explanation
    response = client.get(f"/evaluations/{eval_id}/explanation")
    assert response.status_code == 200
    assert response.json()["strengths"] == "Good structure"


def test_student_access_other_evaluation():
    student_id = uuid.uuid4()
    other_student_id = uuid.uuid4()
    sheet_id = uuid.uuid4()
    eval_id = uuid.uuid4()

    mock_user.email = "student@example.com"
    mock_user.role = "student"

    students_db[student_id] = StudentModel(
        id=student_id,
        email="student@example.com",
        student_number="S123",
        full_name="Student One"
    )

    # Other student's resource
    answer_sheets_db[sheet_id] = AnswerSheetModel(
        id=sheet_id,
        student_id=other_student_id,
        exam_id=uuid.uuid4(),
        original_filename="test.pdf",
        stored_filename="stored.pdf",
        file_path="paths",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.VERIFIED
    )

    evaluations_db[eval_id] = EvaluationModel(
        id=eval_id,
        answer_sheet_id=sheet_id,
        question_id=uuid.uuid4(),
        ai_score=8.5,
        final_score=8.5,
        explanation={"strengths": "Good structure"}
    )

    # 1. Test GET /evaluations/{id} -> Forbidden
    response = client.get(f"/evaluations/{eval_id}")
    assert response.status_code == 403

    # 2. Test GET /evaluations/{id}/explanation -> Forbidden
    response = client.get(f"/evaluations/{eval_id}/explanation")
    assert response.status_code == 403


def test_student_access_own_answer_sheet():
    student_id = uuid.uuid4()
    sheet_id = uuid.uuid4()

    mock_user.email = "student@example.com"
    mock_user.role = "student"

    students_db[student_id] = StudentModel(
        id=student_id,
        email="student@example.com",
        student_number="S123",
        full_name="Student One"
    )

    answer_sheets_db[sheet_id] = AnswerSheetModel(
        id=sheet_id,
        student_id=student_id,
        exam_id=uuid.uuid4(),
        original_filename="test.pdf",
        stored_filename="stored.pdf",
        file_path="paths",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.VERIFIED
    )

    # 1. Test GET /answer-sheets/{id} -> Allowed
    response = client.get(f"/answer-sheets/{sheet_id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(sheet_id)

    # 2. Test GET /answer-sheets/{id}/evaluations -> Allowed
    response = client.get(f"/answer-sheets/{sheet_id}/evaluations")
    assert response.status_code == 200


def test_student_access_other_answer_sheet():
    student_id = uuid.uuid4()
    other_student_id = uuid.uuid4()
    sheet_id = uuid.uuid4()

    mock_user.email = "student@example.com"
    mock_user.role = "student"

    students_db[student_id] = StudentModel(
        id=student_id,
        email="student@example.com",
        student_number="S123",
        full_name="Student One"
    )

    answer_sheets_db[sheet_id] = AnswerSheetModel(
        id=sheet_id,
        student_id=other_student_id,
        exam_id=uuid.uuid4(),
        original_filename="test.pdf",
        stored_filename="stored.pdf",
        file_path="paths",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.VERIFIED
    )

    # 1. Test GET /answer-sheets/{id} -> Forbidden
    response = client.get(f"/answer-sheets/{sheet_id}")
    assert response.status_code == 403

    # 2. Test GET /answer-sheets/{id}/evaluations -> Forbidden
    response = client.get(f"/answer-sheets/{sheet_id}/evaluations")
    assert response.status_code == 403


def test_student_list_answer_sheets_filters_automatically():
    student_id = uuid.uuid4()
    other_student_id = uuid.uuid4()

    mock_user.email = "student@example.com"
    mock_user.role = "student"

    students_db[student_id] = StudentModel(
        id=student_id,
        email="student@example.com",
        student_number="S123",
        full_name="Student One"
    )

    sheet_own = AnswerSheetModel(
        id=uuid.uuid4(),
        student_id=student_id,
        exam_id=uuid.uuid4(),
        original_filename="own.pdf",
        stored_filename="own.pdf",
        file_path="paths",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="own_hash",
        status=AnswerSheetStatus.VERIFIED
    )
    sheet_other = AnswerSheetModel(
        id=uuid.uuid4(),
        student_id=other_student_id,
        exam_id=uuid.uuid4(),
        original_filename="other.pdf",
        stored_filename="other.pdf",
        file_path="paths",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="other_hash",
        status=AnswerSheetStatus.VERIFIED
    )

    answer_sheets_db[sheet_own.id] = sheet_own
    answer_sheets_db[sheet_other.id] = sheet_other

    response = client.get("/answer-sheets")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["original_filename"] == "own.pdf"


def test_student_exam_results_forbidden():
    mock_user.role = "student"
    exam_id = uuid.uuid4()

    response = client.get(f"/results/exams/{exam_id}")
    assert response.status_code == 403


def test_teacher_exam_results_allowed():
    mock_user.role = UserRole.TEACHER
    exam_id = uuid.uuid4()

    exams_db[exam_id] = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="History",
        total_marks=100,
        passing_marks=40
    )

    response = client.get(f"/results/exams/{exam_id}")
    assert response.status_code == 200


# ── PUBLICATION FILTERING TESTS ───────────────────────────────────────────────

def test_student_results_publication_filtering():
    student_id = uuid.uuid4()
    exam_published_id = uuid.uuid4()
    exam_unpublished_id = uuid.uuid4()

    mock_user.email = "student@example.com"
    mock_user.role = "student"

    students_db[student_id] = StudentModel(
        id=student_id,
        email="student@example.com",
        student_number="S123",
        full_name="Student One",
        class_section="A"
    )

    exams_db[exam_published_id] = ExamModel(
        id=exam_published_id,
        subject_id=uuid.uuid4(),
        title="Published Exam",
        total_marks=100,
        passing_marks=40
    )

    exams_db[exam_unpublished_id] = ExamModel(
        id=exam_unpublished_id,
        subject_id=uuid.uuid4(),
        title="Unpublished Exam",
        total_marks=100,
        passing_marks=40
    )

    res_pub = FinalResultModel(
        id=uuid.uuid4(),
        student_id=student_id,
        exam_id=exam_published_id,
        percentage=85.0,
        grade="A",
        pass_fail_status=PassFailStatus.PASS,
        is_published=True
    )

    res_unpub = FinalResultModel(
        id=uuid.uuid4(),
        student_id=student_id,
        exam_id=exam_unpublished_id,
        percentage=95.0,
        grade="A+",
        pass_fail_status=PassFailStatus.PASS,
        is_published=False
    )

    final_results_db[res_pub.id] = res_pub
    final_results_db[res_unpub.id] = res_unpub

    # 1. Request as student: Only published visible
    response = client.get(f"/results/students/{student_id}")
    assert response.status_code == 200
    history = response.json()["history"]
    assert len(history) == 1
    assert history[0]["exam_title"] == "Published Exam"

    # 2. Request as teacher: All visible
    mock_user.role = UserRole.TEACHER
    response = client.get(f"/results/students/{student_id}")
    assert response.status_code == 200
    history = response.json()["history"]
    assert len(history) == 2


def test_student_transcript_publication_filtering():
    student_id = uuid.uuid4()
    exam_published_id = uuid.uuid4()
    exam_unpublished_id = uuid.uuid4()

    mock_user.email = "student@example.com"
    mock_user.role = "student"

    students_db[student_id] = StudentModel(
        id=student_id,
        email="student@example.com",
        student_number="S123",
        full_name="Student One",
        class_section="A"
    )

    exams_db[exam_published_id] = ExamModel(
        id=exam_published_id,
        subject_id=uuid.uuid4(),
        title="Published Exam",
        total_marks=100,
        passing_marks=40
    )

    exams_db[exam_unpublished_id] = ExamModel(
        id=exam_unpublished_id,
        subject_id=uuid.uuid4(),
        title="Unpublished Exam",
        total_marks=100,
        passing_marks=40
    )

    res_pub = FinalResultModel(
        id=uuid.uuid4(),
        student_id=student_id,
        exam_id=exam_published_id,
        percentage=80.0,
        grade="B",
        pass_fail_status=PassFailStatus.PASS,
        is_published=True
    )

    res_unpub = FinalResultModel(
        id=uuid.uuid4(),
        student_id=student_id,
        exam_id=exam_unpublished_id,
        percentage=90.0,
        grade="A",
        pass_fail_status=PassFailStatus.PASS,
        is_published=False
    )

    final_results_db[res_pub.id] = res_pub
    final_results_db[res_unpub.id] = res_unpub

    # Mock PDF service to return custom text we can check
    with patch("app.infrastructure.reports.weasyprint_pdf_service.WeasyPrintPDFService.generate_pdf") as mock_pdf:
        mock_pdf.return_value = b"MOCK PDF BYTES"

        # 1. As student: expect total_exams = 1, average = 80
        response = client.get(f"/results/students/{student_id}/transcript/pdf")
        assert response.status_code == 200
        mock_pdf.assert_called_once()
        context = mock_pdf.call_args[0][1]
        assert context["total_exams"] == 1
        assert context["average_percentage"] == 80.0

        mock_pdf.reset_mock()

        # 2. As teacher: expect total_exams = 2, average = 85
        mock_user.role = UserRole.TEACHER
        response = client.get(f"/results/students/{student_id}/transcript/pdf")
        assert response.status_code == 200
        mock_pdf.assert_called_once()
        context = mock_pdf.call_args[0][1]
        assert context["total_exams"] == 2
        assert context["average_percentage"] == 85.0


def test_student_csv_export_publication_filtering():
    student_id = uuid.uuid4()
    exam_published_id = uuid.uuid4()
    exam_unpublished_id = uuid.uuid4()

    mock_user.email = "student@example.com"
    mock_user.role = "student"

    students_db[student_id] = StudentModel(
        id=student_id,
        email="student@example.com",
        student_number="S123",
        full_name="Student One",
        class_section="A"
    )

    exams_db[exam_published_id] = ExamModel(
        id=exam_published_id,
        subject_id=uuid.uuid4(),
        title="Published Exam",
        total_marks=100,
        passing_marks=40
    )

    exams_db[exam_unpublished_id] = ExamModel(
        id=exam_unpublished_id,
        subject_id=uuid.uuid4(),
        title="Unpublished Exam",
        total_marks=100,
        passing_marks=40
    )

    res_pub = FinalResultModel(
        id=uuid.uuid4(),
        student_id=student_id,
        exam_id=exam_published_id,
        percentage=80.0,
        grade="B",
        pass_fail_status=PassFailStatus.PASS,
        is_published=True
    )

    res_unpub = FinalResultModel(
        id=uuid.uuid4(),
        student_id=student_id,
        exam_id=exam_unpublished_id,
        percentage=90.0,
        grade="A",
        pass_fail_status=PassFailStatus.PASS,
        is_published=False
    )

    final_results_db[res_pub.id] = res_pub
    final_results_db[res_unpub.id] = res_unpub

    # 1. As student: expect CSV payload with only published row
    response = client.get(f"/results/students/{student_id}/export/csv")
    assert response.status_code == 200
    csv_text = response.text
    assert "Published Exam" in csv_text
    assert "Unpublished Exam" not in csv_text

    # 2. As teacher: expect CSV payload with both rows
    mock_user.role = UserRole.TEACHER
    response = client.get(f"/results/students/{student_id}/export/csv")
    assert response.status_code == 200
    csv_text = response.text
    assert "Published Exam" in csv_text
    assert "Unpublished Exam" in csv_text


# ── PLAGIARISM RESTRICTIONS TESTS ────────────────────────────────────────────

def test_plagiarism_endpoints_student_forbidden():
    mock_user.role = "student"
    exam_id = uuid.uuid4()
    sheet_id = uuid.uuid4()
    report_id = uuid.uuid4()

    # GET /plagiarism/reports
    response = client.get("/plagiarism/reports")
    assert response.status_code == 403

    # GET /plagiarism/exams/{exam_id}/summary
    response = client.get(f"/plagiarism/exams/{exam_id}/summary")
    assert response.status_code == 403

    # GET /plagiarism/{answer_sheet_id}
    response = client.get(f"/plagiarism/{sheet_id}")
    assert response.status_code == 403

    # GET /plagiarism/{report_id}/similarities
    response = client.get(f"/plagiarism/{report_id}/similarities")
    assert response.status_code == 403

    # POST /plagiarism/{report_id}/review
    response = client.post(f"/plagiarism/{report_id}/review", json={"status": "FALSE_POSITIVE", "teacher_notes": "None"})
    assert response.status_code == 403


def test_plagiarism_endpoints_teacher_allowed():
    mock_user.role = UserRole.TEACHER
    exam_id = uuid.uuid4()
    sheet_id = uuid.uuid4()
    report_id = uuid.uuid4()

    # Stub execute output to prevent crashes on DB calls
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_execute_result

    # GET /plagiarism/reports
    response = client.get("/plagiarism/reports")
    assert response.status_code == 200


# ── FILE UPLOAD SIGNATURE HARDENING TESTS ─────────────────────────────────────

def test_upload_valid_pdf_accepted():
    mock_user.role = UserRole.TEACHER
    exam_id = uuid.uuid4()
    
    exam_orm = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Math Midterm",
        total_marks=100,
        passing_marks=40
    )
    exams_db[exam_id] = exam_orm

    student_id = uuid.uuid4()
    students_db[student_id] = StudentModel(
        id=student_id,
        email="student@example.com",
        student_number="sheet",
        full_name="Test Student",
        class_section="A"
    )

    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF"
    file_payload = [
        ("files", ("sheet.pdf", io.BytesIO(pdf_bytes), "application/pdf"))
    ]

    with patch("app.tasks.ocr_tasks.process_answer_sheet_ocr.delay"):
        response = client.post(
            "/answer-sheets/upload",
            data={"exam_id": str(exam_id)},
            files=file_payload
        )
    assert response.status_code == 201


def test_upload_valid_png_accepted():
    mock_user.role = UserRole.TEACHER
    exam_id = uuid.uuid4()
    
    exam_orm = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Math Midterm",
        total_marks=100,
        passing_marks=40
    )
    exams_db[exam_id] = exam_orm

    student_id = uuid.uuid4()
    students_db[student_id] = StudentModel(
        id=student_id,
        email="student@example.com",
        student_number="sheet",
        full_name="Test Student",
        class_section="A"
    )

    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    file_payload = [
        ("files", ("sheet.png", io.BytesIO(png_bytes), "image/png"))
    ]

    with patch("app.tasks.ocr_tasks.process_answer_sheet_ocr.delay"):
        response = client.post(
            "/answer-sheets/upload",
            data={"exam_id": str(exam_id)},
            files=file_payload
        )
    assert response.status_code == 201


def test_upload_valid_jpeg_accepted():
    mock_user.role = UserRole.TEACHER
    exam_id = uuid.uuid4()
    
    exam_orm = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Math Midterm",
        total_marks=100,
        passing_marks=40
    )
    exams_db[exam_id] = exam_orm

    student_id = uuid.uuid4()
    students_db[student_id] = StudentModel(
        id=student_id,
        email="student@example.com",
        student_number="sheet",
        full_name="Test Student",
        class_section="A"
    )

    jpeg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    file_payload = [
        ("files", ("sheet.jpg", io.BytesIO(jpeg_bytes), "image/jpeg"))
    ]

    with patch("app.tasks.ocr_tasks.process_answer_sheet_ocr.delay"):
        response = client.post(
            "/answer-sheets/upload",
            data={"exam_id": str(exam_id)},
            files=file_payload
        )
    assert response.status_code == 201


def test_upload_spoofed_pdf_rejected():
    mock_user.role = UserRole.TEACHER
    exam_id = uuid.uuid4()
    
    exam_orm = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Math Midterm",
        total_marks=100,
        passing_marks=40
    )
    exams_db[exam_id] = exam_orm

    # Content is plain text / spoofed instead of binary signature
    bad_pdf_bytes = b"This is not a real PDF file contents"
    file_payload = [
        ("files", ("sheet.pdf", io.BytesIO(bad_pdf_bytes), "application/pdf"))
    ]

    response = client.post(
        "/answer-sheets/upload",
        data={"exam_id": str(exam_id)},
        files=file_payload
    )
    assert response.status_code == 400
    assert "unsupported file format" in response.json()["detail"].lower()


def test_upload_renamed_executable_rejected():
    mock_user.role = UserRole.TEACHER
    exam_id = uuid.uuid4()
    
    exam_orm = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Math Midterm",
        total_marks=100,
        passing_marks=40
    )
    exams_db[exam_id] = exam_orm

    # Executable renamed to PDF
    exe_bytes = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff"
    file_payload = [
        ("files", ("sheet.pdf", io.BytesIO(exe_bytes), "application/pdf"))
    ]

    response = client.post(
        "/answer-sheets/upload",
        data={"exam_id": str(exam_id)},
        files=file_payload
    )
    assert response.status_code == 400
    assert "unsupported file format" in response.json()["detail"].lower()


def test_upload_spoofed_png_rejected():
    mock_user.role = UserRole.TEACHER
    exam_id = uuid.uuid4()
    
    exam_orm = ExamModel(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Math Midterm",
        total_marks=100,
        passing_marks=40
    )
    exams_db[exam_id] = exam_orm

    # PNG extension but fake contents
    bad_png_bytes = b"Spoofed PNG contents text"
    file_payload = [
        ("files", ("sheet.png", io.BytesIO(bad_png_bytes), "image/png"))
    ]

    response = client.post(
        "/answer-sheets/upload",
        data={"exam_id": str(exam_id)},
        files=file_payload
    )
    assert response.status_code == 400
    assert "unsupported file format" in response.json()["detail"].lower()
