"""
tests/unit/application/test_exam_use_cases.py — Unit Tests for Exams Use Cases
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.application.use_cases.exams.create_exam_use_case import CreateExamUseCase
from app.application.use_cases.exams.update_exam_use_case import UpdateExamUseCase
from app.application.use_cases.exams.delete_exam_use_case import DeleteExamUseCase
from app.application.use_cases.exams.get_exam_use_case import GetExamUseCase
from app.application.use_cases.exams.list_exams_use_case import ListExamsUseCase

from app.domain.entities.exam import Exam
from app.domain.entities.subject import Subject
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.subject_repository import SubjectRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository

from app.domain.exceptions.domain_exception import (
    EntityNotFoundException,
    BusinessRuleViolationException,
)
from app.core.constants import ExamStatus, AuditAction, AuditStatus
from app.core.pagination import PaginationParams, PaginatedResponse


@pytest.fixture
def mock_exam_repo():
    repo = MagicMock(spec=ExamRepository)
    repo.save = AsyncMock()
    repo.delete = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.list_exams = AsyncMock()
    return repo


@pytest.fixture
def mock_subject_repo():
    repo = MagicMock(spec=SubjectRepository)
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_audit_repo():
    repo = MagicMock(spec=AuditLogRepository)
    repo.save = AsyncMock()
    return repo


@pytest.mark.asyncio
async def test_create_exam_success(mock_exam_repo, mock_subject_repo, mock_audit_repo):
    subject_id = uuid.uuid4()
    creator_id = uuid.uuid4()
    
    subject = Subject(
        id=subject_id,
        name="Science",
        code="SCI101",
        created_by=creator_id,
        description="Intro to Science"
    )
    mock_subject_repo.get_by_id.return_value = subject

    exam_id = uuid.uuid4()
    saved_exam_mock = Exam(
        id=exam_id,
        subject_id=subject_id,
        title="Final Exam",
        exam_date=date(2026, 6, 21),
        total_marks=100,
        passing_marks=40,
        duration_minutes=120,
        status=ExamStatus.DRAFT,
        scoring_config={},
        created_by=creator_id
    )
    mock_exam_repo.save.return_value = saved_exam_mock

    use_case = CreateExamUseCase(
        exam_repo=mock_exam_repo,
        subject_repo=mock_subject_repo,
        audit_repo=mock_audit_repo
    )

    exam = await use_case.execute(
        subject_id=subject_id,
        title="Final Exam",
        exam_date=date(2026, 6, 21),
        total_marks=100,
        passing_marks=40,
        created_by=creator_id,
        duration_minutes=120,
        status=ExamStatus.DRAFT,
        scoring_config={},
        ip_address="192.168.1.1",
        user_agent="PyTest"
    )

    assert exam.id == exam_id
    assert exam.title == "Final Exam"
    assert exam.total_marks == 100
    mock_subject_repo.get_by_id.assert_called_once_with(subject_id)
    mock_exam_repo.save.assert_called_once()
    mock_audit_repo.save.assert_called_once()
    
    saved_log = mock_audit_repo.save.call_args[0][0]
    assert saved_log.action == AuditAction.EXAM_CREATED
    assert saved_log.status == AuditStatus.SUCCESS
    assert saved_log.user_id == creator_id


@pytest.mark.asyncio
async def test_create_exam_subject_not_found(mock_exam_repo, mock_subject_repo, mock_audit_repo):
    subject_id = uuid.uuid4()
    mock_subject_repo.get_by_id.return_value = None

    use_case = CreateExamUseCase(
        exam_repo=mock_exam_repo,
        subject_repo=mock_subject_repo,
        audit_repo=mock_audit_repo
    )

    with pytest.raises(EntityNotFoundException) as exc_info:
        await use_case.execute(
            subject_id=subject_id,
            title="Final Exam",
            exam_date=date(2026, 6, 21),
            total_marks=100,
            passing_marks=40,
            created_by=uuid.uuid4()
        )

    assert exc_info.value.entity_type == "Subject"
    mock_exam_repo.save.assert_not_called()
    mock_audit_repo.save.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "total,passing,rule_sub_string",
    [
        (0, 40, "total_marks must be greater than 0"),
        (100, 0, "passing_marks must be greater than 0"),
        (100, 101, "passing_marks cannot exceed total_marks"),
    ]
)
async def test_create_exam_validation_failures(
    mock_exam_repo, mock_subject_repo, mock_audit_repo, total, passing, rule_sub_string
):
    subject_id = uuid.uuid4()
    subject = Subject(
        id=subject_id,
        name="Science",
        code="SCI101",
        created_by=uuid.uuid4()
    )
    mock_subject_repo.get_by_id.return_value = subject

    use_case = CreateExamUseCase(
        exam_repo=mock_exam_repo,
        subject_repo=mock_subject_repo,
        audit_repo=mock_audit_repo
    )

    with pytest.raises(BusinessRuleViolationException) as exc_info:
        await use_case.execute(
            subject_id=subject_id,
            title="Final Exam",
            exam_date=date(2026, 6, 21),
            total_marks=total,
            passing_marks=passing,
            created_by=uuid.uuid4()
        )

    assert rule_sub_string in exc_info.value.rule
    mock_exam_repo.save.assert_not_called()
    mock_audit_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_update_exam_success(mock_exam_repo, mock_subject_repo, mock_audit_repo):
    exam_id = uuid.uuid4()
    subject_id = uuid.uuid4()
    updater_id = uuid.uuid4()

    original_exam = Exam(
        id=exam_id,
        subject_id=subject_id,
        title="Midterm",
        exam_date=date(2026, 6, 1),
        total_marks=50,
        passing_marks=20,
        duration_minutes=60,
        status=ExamStatus.DRAFT,
        created_by=updater_id
    )
    mock_exam_repo.get_by_id.return_value = original_exam
    mock_exam_repo.save.side_effect = lambda e: e

    use_case = UpdateExamUseCase(
        exam_repo=mock_exam_repo,
        subject_repo=mock_subject_repo,
        audit_repo=mock_audit_repo
    )

    updated = await use_case.execute(
        exam_id=exam_id,
        updater_id=updater_id,
        title="Updated Midterm",
        total_marks=60,
        passing_marks=25,
        ip_address="127.0.0.1",
        user_agent="Firefox"
    )

    assert updated.title == "Updated Midterm"
    assert updated.total_marks == 60
    assert updated.passing_marks == 25
    mock_exam_repo.get_by_id.assert_called_once_with(exam_id)
    mock_exam_repo.save.assert_called_once_with(original_exam)
    mock_audit_repo.save.assert_called_once()

    saved_log = mock_audit_repo.save.call_args[0][0]
    assert saved_log.action == AuditAction.EXAM_UPDATED
    assert saved_log.status == AuditStatus.SUCCESS
    assert saved_log.old_values["title"] == "Midterm"
    assert saved_log.new_values["title"] == "Updated Midterm"


@pytest.mark.asyncio
async def test_update_exam_not_found(mock_exam_repo, mock_subject_repo, mock_audit_repo):
    exam_id = uuid.uuid4()
    mock_exam_repo.get_by_id.return_value = None

    use_case = UpdateExamUseCase(
        exam_repo=mock_exam_repo,
        subject_repo=mock_subject_repo,
        audit_repo=mock_audit_repo
    )

    with pytest.raises(EntityNotFoundException) as exc_info:
        await use_case.execute(
            exam_id=exam_id,
            updater_id=uuid.uuid4(),
            title="Updated Midterm"
        )

    assert exc_info.value.entity_type == "Exam"
    mock_exam_repo.save.assert_not_called()
    mock_audit_repo.save.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "total,passing,rule_sub_string",
    [
        (0, 20, "total_marks must be greater than 0"),
        (50, 0, "passing_marks must be greater than 0"),
        (50, 60, "passing_marks cannot exceed total_marks"),
    ]
)
async def test_update_exam_validation_failures(
    mock_exam_repo, mock_subject_repo, mock_audit_repo, total, passing, rule_sub_string
):
    exam_id = uuid.uuid4()
    original_exam = Exam(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Midterm",
        exam_date=date(2026, 6, 1),
        total_marks=50,
        passing_marks=20,
        created_by=uuid.uuid4()
    )
    mock_exam_repo.get_by_id.return_value = original_exam

    use_case = UpdateExamUseCase(
        exam_repo=mock_exam_repo,
        subject_repo=mock_subject_repo,
        audit_repo=mock_audit_repo
    )

    with pytest.raises(BusinessRuleViolationException) as exc_info:
        await use_case.execute(
            exam_id=exam_id,
            updater_id=uuid.uuid4(),
            total_marks=total,
            passing_marks=passing
        )

    assert rule_sub_string in exc_info.value.rule
    mock_exam_repo.save.assert_not_called()
    mock_audit_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_delete_exam_success(mock_exam_repo, mock_audit_repo):
    exam_id = uuid.uuid4()
    deleter_id = uuid.uuid4()

    exam = Exam(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Delete Me",
        exam_date=date(2026, 6, 1),
        total_marks=50,
        passing_marks=20,
        created_by=deleter_id
    )
    mock_exam_repo.get_by_id.return_value = exam
    mock_exam_repo.delete.return_value = True

    use_case = DeleteExamUseCase(
        exam_repo=mock_exam_repo,
        audit_repo=mock_audit_repo
    )

    success = await use_case.execute(
        exam_id=exam_id,
        deleter_id=deleter_id,
        ip_address="127.0.0.1"
    )

    assert success is True
    mock_exam_repo.get_by_id.assert_called_once_with(exam_id)
    mock_exam_repo.delete.assert_called_once_with(exam_id)
    mock_audit_repo.save.assert_called_once()
    
    saved_log = mock_audit_repo.save.call_args[0][0]
    assert saved_log.action == AuditAction.EXAM_DELETED
    assert saved_log.status == AuditStatus.SUCCESS


@pytest.mark.asyncio
async def test_delete_exam_not_found(mock_exam_repo, mock_audit_repo):
    exam_id = uuid.uuid4()
    mock_exam_repo.get_by_id.return_value = None

    use_case = DeleteExamUseCase(
        exam_repo=mock_exam_repo,
        audit_repo=mock_audit_repo
    )

    with pytest.raises(EntityNotFoundException) as exc_info:
        await use_case.execute(
            exam_id=exam_id,
            deleter_id=uuid.uuid4()
        )

    assert exc_info.value.entity_type == "Exam"
    mock_exam_repo.delete.assert_not_called()
    mock_audit_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_delete_exam_failed(mock_exam_repo, mock_audit_repo):
    exam_id = uuid.uuid4()
    exam = Exam(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Delete Me",
        exam_date=date(2026, 6, 1),
        total_marks=50,
        passing_marks=20,
        created_by=uuid.uuid4()
    )
    mock_exam_repo.get_by_id.return_value = exam
    mock_exam_repo.delete.return_value = False

    use_case = DeleteExamUseCase(
        exam_repo=mock_exam_repo,
        audit_repo=mock_audit_repo
    )

    success = await use_case.execute(
        exam_id=exam_id,
        deleter_id=uuid.uuid4()
    )

    assert success is False
    mock_exam_repo.delete.assert_called_once_with(exam_id)
    mock_audit_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_get_exam_success(mock_exam_repo):
    exam_id = uuid.uuid4()
    exam = Exam(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Get Me",
        exam_date=date(2026, 6, 1),
        total_marks=50,
        passing_marks=20,
        created_by=uuid.uuid4()
    )
    mock_exam_repo.get_by_id.return_value = exam

    use_case = GetExamUseCase(exam_repo=mock_exam_repo)
    result = await use_case.execute(exam_id)

    assert result.id == exam_id
    mock_exam_repo.get_by_id.assert_called_once_with(exam_id)


@pytest.mark.asyncio
async def test_get_exam_not_found(mock_exam_repo):
    exam_id = uuid.uuid4()
    mock_exam_repo.get_by_id.return_value = None

    use_case = GetExamUseCase(exam_repo=mock_exam_repo)

    with pytest.raises(EntityNotFoundException) as exc_info:
        await use_case.execute(exam_id)

    assert exc_info.value.entity_type == "Exam"


@pytest.mark.asyncio
async def test_list_exams_success(mock_exam_repo):
    pagination = PaginationParams(page=1, limit=10)
    exams_list = [
        Exam(
            id=uuid.uuid4(),
            subject_id=uuid.uuid4(),
            title="Exam 1",
            exam_date=date(2026, 6, 1),
            total_marks=50,
            passing_marks=20,
            created_by=uuid.uuid4()
        ),
        Exam(
            id=uuid.uuid4(),
            subject_id=uuid.uuid4(),
            title="Exam 2",
            exam_date=date(2026, 6, 2),
            total_marks=100,
            passing_marks=40,
            created_by=uuid.uuid4()
        )
    ]
    paginated_resp = PaginatedResponse(
        items=exams_list,
        total=2,
        page=1,
        limit=10
    )
    mock_exam_repo.list_exams.return_value = paginated_resp

    use_case = ListExamsUseCase(exam_repo=mock_exam_repo)
    subject_id = uuid.uuid4()
    result = await use_case.execute(
        pagination=pagination,
        search="Exam",
        subject_id=subject_id,
        status="draft"
    )

    assert result.total == 2
    assert len(result.items) == 2
    mock_exam_repo.list_exams.assert_called_once_with(
        pagination=pagination,
        search="Exam",
        subject_id=subject_id,
        status="draft"
    )
