"""
tests/unit/application/test_results_use_cases.py — Unit Tests for Results Use Cases
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.domain.entities.final_result import FinalResult
from app.domain.entities.answer_sheet import AnswerSheet
from app.domain.entities.exam import Exam
from app.domain.entities.student import Student
from app.domain.entities.subject import Subject
from app.domain.entities.evaluation import Evaluation

from app.application.services.final_result_synchronization_service import FinalResultSynchronizationService
from app.application.use_cases.results.get_results_dashboard_use_case import GetResultsDashboardUseCase
from app.application.use_cases.results.get_exam_results_use_case import GetExamResultsUseCase
from app.application.use_cases.results.get_student_results_use_case import GetStudentResultsUseCase
from app.application.use_cases.results.publish_exam_results_use_case import PublishExamResultsUseCase

from app.core.constants import AnswerSheetStatus, PassFailStatus, AuditAction, AuditStatus
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException


@pytest.fixture
def mock_repos():
    return {
        "final_result_repo": MagicMock(),
        "answer_sheet_repo": MagicMock(),
        "exam_repo": MagicMock(),
        "student_repo": MagicMock(),
        "subject_repo": MagicMock(),
        "question_repo": MagicMock(),
        "evaluation_repo": MagicMock(),
        "audit_repo": MagicMock()
    }


# ── Synchronization Service Tests ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_synchronization_service_creation_and_grading(mock_repos):
    final_result_repo = mock_repos["final_result_repo"]
    answer_sheet_repo = mock_repos["answer_sheet_repo"]
    exam_repo = mock_repos["exam_repo"]
    question_repo = mock_repos["question_repo"]
    evaluation_repo = mock_repos["evaluation_repo"]

    sheet_id = uuid.uuid4()
    exam_id = uuid.uuid4()
    student_id = uuid.uuid4()

    # Stub models
    mock_sheet = AnswerSheet(
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
        status=AnswerSheetStatus.VERIFIED
    )
    mock_exam = Exam(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Math Exam",
        exam_date=datetime.now().date(),
        total_marks=100,
        passing_marks=40,
        created_by=uuid.uuid4()
    )
    
    mock_questions = [
        MagicMock(marks=50),
        MagicMock(marks=50)
    ]

    # Q1: Verified with teacher override
    # Q2: Unverified, uses AI score
    mock_evals = [
        Evaluation(
            id=uuid.uuid4(),
            answer_sheet_id=sheet_id,
            question_mapping_id=uuid.uuid4(),
            question_id=uuid.uuid4(),
            model_answer_id=uuid.uuid4(),
            max_marks=50.0,
            ai_score=40.0,
            teacher_score=45.0, # Verified override
            is_verified=True
        ),
        Evaluation(
            id=uuid.uuid4(),
            answer_sheet_id=sheet_id,
            question_mapping_id=uuid.uuid4(),
            question_id=uuid.uuid4(),
            model_answer_id=uuid.uuid4(),
            max_marks=50.0,
            ai_score=35.0, # Unverified AI fallback
            is_verified=False
        )
    ]

    answer_sheet_repo.get_by_id = AsyncMock(return_value=mock_sheet)
    exam_repo.get_by_id = AsyncMock(return_value=mock_exam)
    question_repo.get_by_id = AsyncMock()
    question_repo.get_by_exam_id = AsyncMock(return_value=mock_questions)
    evaluation_repo.get_by_answer_sheet_id = AsyncMock(return_value=mock_evals)
    
    # Mock no existing final result
    final_result_repo.get_by_answer_sheet_id = AsyncMock(return_value=None)
    final_result_repo.save = AsyncMock(side_effect=lambda x: x)

    sync_service = FinalResultSynchronizationService(
        final_result_repo=final_result_repo,
        evaluation_repo=evaluation_repo,
        answer_sheet_repo=answer_sheet_repo,
        question_repo=question_repo,
        exam_repo=exam_repo
    )

    result = await sync_service.sync(sheet_id)

    # 45 (verified override) + 35 (ai fallback) = 80 obtained
    assert result.total_marks_obtained == 80.0
    assert result.total_marks_possible == 100
    assert result.percentage == 80.0
    assert result.grade == "A+"  # 80% matches A+ [80%, 90%)
    assert result.pass_fail_status == PassFailStatus.PASS
    assert result.is_published is False
    final_result_repo.save.assert_called_once()


# ── Dashboard Use Case Tests ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dashboard_aggregation_maths(mock_repos):
    final_result_repo = mock_repos["final_result_repo"]
    
    # Mock SQL session count queries
    mock_session = MagicMock()
    mock_session.execute = AsyncMock(side_effect=[
        MagicMock(scalar=lambda: 10), # total_students_evaluated
        MagicMock(scalar=lambda: 6),  # total_published
        MagicMock(scalar=lambda: 75.0), # average_score
        MagicMock(scalar=lambda: 8)   # pass_count
    ])
    final_result_repo.session = mock_session

    use_case = GetResultsDashboardUseCase(final_result_repo)
    dashboard = await use_case.execute()

    assert dashboard["total_students_evaluated"] == 10
    assert dashboard["total_published"] == 6
    assert dashboard["pending_publication"] == 4
    assert dashboard["average_score"] == 75.0
    assert dashboard["pass_rate"] == 80.0
    assert dashboard["fail_rate"] == 20.0


# ── Exam Results Use Case Tests ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_exam_results_pagination_and_search_success(mock_repos):
    final_result_repo = mock_repos["final_result_repo"]
    answer_sheet_repo = mock_repos["answer_sheet_repo"]
    exam_repo = mock_repos["exam_repo"]
    student_repo = mock_repos["student_repo"]

    exam_id = uuid.uuid4()
    mock_exam = Exam(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Chemistry Exam",
        exam_date=datetime.now().date(),
        total_marks=100,
        passing_marks=40,
        created_by=uuid.uuid4()
    )

    mock_student = Student(
        id=uuid.uuid4(),
        student_number="S123",
        full_name="Alice Smith",
        email="alice@test.com"
    )

    mock_sheet = AnswerSheet(
        id=uuid.uuid4(),
        exam_id=exam_id,
        student_id=mock_student.id,
        uploaded_by=uuid.uuid4(),
        original_filename="a.pdf",
        stored_filename="a.pdf",
        file_path="",
        file_size_bytes=100,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.VERIFIED
    )

    mock_result = FinalResult(
        id=uuid.uuid4(),
        answer_sheet_id=mock_sheet.id,
        student_id=mock_student.id,
        exam_id=exam_id,
        total_marks_obtained=75.0,
        total_marks_possible=100,
        percentage=75.0,
        grade="A",
        pass_fail_status=PassFailStatus.PASS
    )

    exam_repo.get_by_id = AsyncMock(return_value=mock_exam)
    answer_sheet_repo.get_all_by_exam_id = AsyncMock(return_value=[mock_sheet])
    final_result_repo.get_by_exam_id = AsyncMock(return_value=[mock_result])
    final_result_repo.get_by_answer_sheet_id = AsyncMock(return_value=mock_result)
    student_repo.get_by_id = AsyncMock(return_value=mock_student)

    sync_service = MagicMock()

    use_case = GetExamResultsUseCase(
        final_result_repo=final_result_repo,
        answer_sheet_repo=answer_sheet_repo,
        exam_repo=exam_repo,
        student_repo=student_repo,
        sync_service=sync_service
    )

    # Test search Alice matches
    response = await use_case.execute(exam_id=exam_id, page=1, page_size=10, search="Alice")
    assert response["total_items"] == 1
    assert response["items"][0]["student_name"] == "Alice Smith"
    assert response["items"][0]["marks_obtained"] == 75.0

    # Test search Bob mismatch
    response_empty = await use_case.execute(exam_id=exam_id, page=1, page_size=10, search="Bob")
    assert response_empty["total_items"] == 0
    assert len(response_empty["items"]) == 0


# ── Student Results Use Case Tests ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_student_results_retrieval(mock_repos):
    final_result_repo = mock_repos["final_result_repo"]
    student_repo = mock_repos["student_repo"]
    exam_repo = mock_repos["exam_repo"]
    subject_repo = mock_repos["subject_repo"]

    student_id = uuid.uuid4()
    mock_student = Student(
        id=student_id,
        student_number="S999",
        full_name="Charlie Brown",
        email="charlie@test.com",
        class_section="A"
    )

    mock_exam = Exam(
        id=uuid.uuid4(),
        subject_id=uuid.uuid4(),
        title="History Quiz",
        exam_date=datetime.now().date(),
        total_marks=50,
        passing_marks=20,
        created_by=uuid.uuid4()
    )

    mock_subject = Subject(
        id=mock_exam.subject_id,
        name="Social Studies",
        code="SOC1",
        created_by=uuid.uuid4()
    )

    mock_result = FinalResult(
        id=uuid.uuid4(),
        answer_sheet_id=uuid.uuid4(),
        student_id=student_id,
        exam_id=mock_exam.id,
        total_marks_obtained=45.0,
        total_marks_possible=50,
        percentage=90.0,
        grade="O",
        pass_fail_status=PassFailStatus.PASS,
        is_published=True
    )

    student_repo.get_by_id = AsyncMock(return_value=mock_student)
    exam_repo.get_by_id = AsyncMock(return_value=mock_exam)
    subject_repo.get_by_id = AsyncMock(return_value=mock_subject)

    # Mock SQL student queries
    final_result_repo.to_entity = lambda x: x
    mock_session = MagicMock()
    mock_session.execute = AsyncMock(return_value=MagicMock(scalars=lambda: MagicMock(all=lambda: [mock_result])))
    final_result_repo.session = mock_session

    use_case = GetStudentResultsUseCase(
        final_result_repo=final_result_repo,
        student_repo=student_repo,
        exam_repo=exam_repo,
        subject_repo=subject_repo
    )

    response = await use_case.execute(student_id)
    assert response["student_name"] == "Charlie Brown"
    assert len(response["history"]) == 1
    assert response["history"][0]["exam_title"] == "History Quiz"
    assert response["history"][0]["subject_name"] == "Social Studies"
    assert response["history"][0]["grade"] == "O"


@pytest.mark.asyncio
async def test_student_results_missing_student(mock_repos):
    student_repo = mock_repos["student_repo"]
    student_repo.get_by_id = AsyncMock(return_value=None)

    use_case = GetStudentResultsUseCase(
        final_result_repo=mock_repos["final_result_repo"],
        student_repo=student_repo,
        exam_repo=mock_repos["exam_repo"],
        subject_repo=mock_repos["subject_repo"]
    )

    with pytest.raises(EntityNotFoundException):
        await use_case.execute(uuid.uuid4())


# ── Publishing Results Use Case Tests ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_publish_exam_results_success(mock_repos):
    final_result_repo = mock_repos["final_result_repo"]
    answer_sheet_repo = mock_repos["answer_sheet_repo"]
    exam_repo = mock_repos["exam_repo"]
    audit_repo = mock_repos["audit_repo"]

    exam_id = uuid.uuid4()
    publisher_id = uuid.uuid4()

    mock_exam = Exam(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Exam Title",
        exam_date=datetime.now().date(),
        total_marks=100,
        passing_marks=40,
        created_by=publisher_id
    )

    mock_sheet = AnswerSheet(
        id=uuid.uuid4(),
        exam_id=exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=publisher_id,
        original_filename="sheet1.pdf",
        stored_filename="sheet1.pdf",
        file_path="",
        file_size_bytes=100,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.VERIFIED,
        plagiarism_flagged=False
    )

    mock_result = FinalResult(
        id=uuid.uuid4(),
        answer_sheet_id=mock_sheet.id,
        student_id=mock_sheet.student_id,
        exam_id=exam_id,
        total_marks_obtained=80.0,
        total_marks_possible=100,
        percentage=80.0,
        grade="A+",
        pass_fail_status=PassFailStatus.PASS,
        is_published=False
    )

    exam_repo.get_by_id = AsyncMock(return_value=mock_exam)
    answer_sheet_repo.get_all_by_exam_id = AsyncMock(return_value=[mock_sheet])
    answer_sheet_repo.save = AsyncMock(return_value=mock_sheet)
    final_result_repo.get_by_exam_id = AsyncMock(return_value=[mock_result])
    final_result_repo.publish_exam_results = AsyncMock(return_value=1)
    audit_repo.save = AsyncMock()

    use_case = PublishExamResultsUseCase(
        final_result_repo=final_result_repo,
        answer_sheet_repo=answer_sheet_repo,
        exam_repo=exam_repo,
        audit_repo=audit_repo
    )

    summary = await use_case.execute(exam_id=exam_id, publisher_id=publisher_id)

    assert summary["published_count"] == 1
    assert mock_sheet.status == AnswerSheetStatus.PUBLISHED
    
    # Audit log verification
    audit_repo.save.assert_called_once()
    saved_audit = audit_repo.save.call_args[0][0]
    assert saved_audit.action == AuditAction.RESULT_PUBLISHED
    assert saved_audit.status == AuditStatus.SUCCESS


@pytest.mark.asyncio
async def test_publish_exam_results_blocked_by_plagiarism(mock_repos):
    answer_sheet_repo = mock_repos["answer_sheet_repo"]
    exam_repo = mock_repos["exam_repo"]

    exam_id = uuid.uuid4()
    publisher_id = uuid.uuid4()

    mock_sheet = AnswerSheet(
        id=uuid.uuid4(),
        exam_id=exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=publisher_id,
        original_filename="plagiarized.pdf",
        stored_filename="plagiarized.pdf",
        file_path="",
        file_size_bytes=100,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.VERIFIED,
        plagiarism_flagged=True # Active plagiarism block!
    )

    exam_repo.get_by_id = AsyncMock(return_value=MagicMock())
    answer_sheet_repo.get_all_by_exam_id = AsyncMock(return_value=[mock_sheet])

    use_case = PublishExamResultsUseCase(
        final_result_repo=mock_repos["final_result_repo"],
        answer_sheet_repo=answer_sheet_repo,
        exam_repo=exam_repo,
        audit_repo=mock_repos["audit_repo"]
    )

    with pytest.raises(BusinessRuleViolationException) as exc_info:
        await use_case.execute(exam_id=exam_id, publisher_id=publisher_id)
    
    assert "plagiarism" in str(exc_info.value)


@pytest.mark.asyncio
async def test_publish_exam_results_unverified_fail(mock_repos):
    answer_sheet_repo = mock_repos["answer_sheet_repo"]
    exam_repo = mock_repos["exam_repo"]

    exam_id = uuid.uuid4()
    publisher_id = uuid.uuid4()

    mock_sheet = AnswerSheet(
        id=uuid.uuid4(),
        exam_id=exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=publisher_id,
        original_filename="unverified.pdf",
        stored_filename="unverified.pdf",
        file_path="",
        file_size_bytes=100,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.EVALUATION_COMPLETED, # Verification incomplete!
        plagiarism_flagged=False
    )

    exam_repo.get_by_id = AsyncMock(return_value=MagicMock())
    answer_sheet_repo.get_all_by_exam_id = AsyncMock(return_value=[mock_sheet])

    use_case = PublishExamResultsUseCase(
        final_result_repo=mock_repos["final_result_repo"],
        answer_sheet_repo=answer_sheet_repo,
        exam_repo=exam_repo,
        audit_repo=mock_repos["audit_repo"]
    )

    with pytest.raises(BusinessRuleViolationException) as exc_info:
        await use_case.execute(exam_id=exam_id, publisher_id=publisher_id)

    assert "incomplete verification" in str(exc_info.value)
