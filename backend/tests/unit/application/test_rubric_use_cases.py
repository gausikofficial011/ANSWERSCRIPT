"""
tests/unit/application/test_rubric_use_cases.py — Unit Tests for Rubrics Use Cases
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.application.use_cases.rubrics.create_rubric_use_case import CreateRubricUseCase
from app.application.use_cases.rubrics.update_rubric_use_case import UpdateRubricUseCase
from app.application.use_cases.rubrics.delete_rubric_use_case import DeleteRubricUseCase
from app.application.use_cases.rubrics.get_rubric_use_case import GetRubricUseCase
from app.application.use_cases.rubrics.list_rubrics_use_case import ListRubricsUseCase

from app.domain.entities.rubric import Rubric
from app.domain.entities.rubric_criterion import RubricCriterion
from app.domain.entities.question import Question
from app.domain.repositories.rubric_repository import RubricRepository
from app.domain.repositories.rubric_criterion_repository import RubricCriterionRepository
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository

from app.domain.exceptions.domain_exception import (
    EntityNotFoundException,
    BusinessRuleViolationException,
)
from app.core.constants import GradingMode, AuditAction, AuditStatus


@pytest.fixture
def mock_rubric_repo():
    repo = MagicMock(spec=RubricRepository)
    repo.save = AsyncMock()
    repo.delete = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.deactivate_all_for_question = AsyncMock()
    repo.list_rubrics = AsyncMock()
    return repo


@pytest.fixture
def mock_criterion_repo():
    repo = MagicMock(spec=RubricCriterionRepository)
    repo.save_batch = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_question_repo():
    repo = MagicMock(spec=QuestionRepository)
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_audit_repo():
    repo = MagicMock(spec=AuditLogRepository)
    repo.save = AsyncMock()
    return repo


@pytest.mark.asyncio
async def test_create_rubric_success(
    mock_rubric_repo, mock_criterion_repo, mock_question_repo, mock_audit_repo
):
    question_id = uuid.uuid4()
    creator_id = uuid.uuid4()

    question = Question(
        id=question_id,
        exam_id=uuid.uuid4(),
        question_number=1,
        question_text="Write a program to reverse a linked list.",
        marks=10,
        question_type="descriptive",
        created_by=creator_id
    )
    mock_question_repo.get_by_id.return_value = question

    rubric_id = uuid.uuid4()
    saved_rubric_mock = Rubric(
        id=rubric_id,
        question_id=question_id,
        title="Coding standards",
        description="Grades based on syntax and comments",
        total_weight=1.0,
        version=1,
        is_active=True,
        grading_mode=GradingMode.AI,
        is_locked=False,
        created_by=creator_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        criteria=[]
    )
    mock_rubric_repo.save.return_value = saved_rubric_mock

    criteria_data = [
        {
            "criterion_name": "Correctness",
            "weight": 0.6,
            "max_marks": 6.0,
            "order_index": 0,
            "criterion_description": "Code runs without errors",
            "expected_keywords": ["list", "reverse"]
        },
        {
            "criterion_name": "Style",
            "weight": 0.4,
            "max_marks": 4.0,
            "order_index": 1,
            "criterion_description": "Clean variables and documentation",
            "expected_keywords": ["comment"]
        }
    ]

    mock_criterion_repo.save_batch.return_value = [
        RubricCriterion(
            id=uuid.uuid4(),
            rubric_id=rubric_id,
            criterion_name=c["criterion_name"],
            criterion_description=c["criterion_description"],
            weight=c["weight"],
            max_marks=c["max_marks"],
            expected_keywords=c["expected_keywords"],
            order_index=c["order_index"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        for c in criteria_data
    ]

    use_case = CreateRubricUseCase(
        rubric_repo=mock_rubric_repo,
        criterion_repo=mock_criterion_repo,
        question_repo=mock_question_repo,
        audit_repo=mock_audit_repo
    )

    rubric = await use_case.execute(
        question_id=question_id,
        title="Coding standards",
        total_weight=1.0,
        grading_mode=GradingMode.AI,
        criteria_data=criteria_data,
        created_by=creator_id,
        description="Grades based on syntax and comments",
        ip_address="192.168.1.1",
        user_agent="PyTest"
    )

    assert rubric.id == rubric_id
    assert rubric.title == "Coding standards"
    assert len(rubric.criteria) == 2
    mock_question_repo.get_by_id.assert_called_once_with(question_id)
    mock_rubric_repo.deactivate_all_for_question.assert_called_once_with(question_id)
    mock_rubric_repo.save.assert_called_once()
    mock_criterion_repo.save_batch.assert_called_once()
    mock_audit_repo.save.assert_called_once()
    saved_log = mock_audit_repo.save.call_args[0][0]
    assert saved_log.action == AuditAction.RUBRIC_CREATED
    assert saved_log.status == AuditStatus.SUCCESS


@pytest.mark.asyncio
async def test_create_rubric_mismatch_weights(
    mock_rubric_repo, mock_criterion_repo, mock_question_repo, mock_audit_repo
):
    question_id = uuid.uuid4()
    creator_id = uuid.uuid4()

    question = Question(
        id=question_id,
        exam_id=uuid.uuid4(),
        question_number=1,
        question_text="Text question.",
        marks=5,
        question_type="descriptive",
        created_by=creator_id
    )
    mock_question_repo.get_by_id.return_value = question

    criteria_data = [
        {
            "criterion_name": "Correctness",
            "weight": 0.6,
            "max_marks": 6.0
        }
    ]

    use_case = CreateRubricUseCase(
        rubric_repo=mock_rubric_repo,
        criterion_repo=mock_criterion_repo,
        question_repo=mock_question_repo,
        audit_repo=mock_audit_repo
    )

    with pytest.raises(BusinessRuleViolationException) as exc_info:
        await use_case.execute(
            question_id=question_id,
            title="Title",
            total_weight=1.0,  # 0.6 sum != 1.0 weight
            grading_mode=GradingMode.AI,
            criteria_data=criteria_data,
            created_by=creator_id
        )

    assert "equal rubric total_weight" in exc_info.value.rule


@pytest.mark.asyncio
async def test_update_rubric_unlocked_direct_save(
    mock_rubric_repo, mock_criterion_repo, mock_audit_repo
):
    rubric_id = uuid.uuid4()
    updater_id = uuid.uuid4()

    rubric = Rubric(
        id=rubric_id,
        question_id=uuid.uuid4(),
        title="Original Title",
        description="Original Desc",
        total_weight=1.0,
        version=1,
        is_active=True,
        grading_mode=GradingMode.AI,
        is_locked=False,  # UNLOCKED
        created_by=updater_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        criteria=[]
    )
    mock_rubric_repo.get_by_id.return_value = rubric
    mock_rubric_repo.save.side_effect = lambda r: r

    use_case = UpdateRubricUseCase(
        rubric_repo=mock_rubric_repo,
        criterion_repo=mock_criterion_repo,
        audit_repo=mock_audit_repo
    )

    updated_rubric = await use_case.execute(
        rubric_id=rubric_id,
        updater_id=updater_id,
        title="Updated Title"
    )

    assert updated_rubric.title == "Updated Title"
    assert updated_rubric.version == 1  # version not changed
    mock_rubric_repo.save.assert_called_once_with(rubric)
    saved_log = mock_audit_repo.save.call_args[0][0]
    assert saved_log.action == AuditAction.RUBRIC_UPDATED
    assert saved_log.status == AuditStatus.SUCCESS


@pytest.mark.asyncio
async def test_update_rubric_locked_creates_new_version(
    mock_rubric_repo, mock_criterion_repo, mock_audit_repo
):
    rubric_id = uuid.uuid4()
    updater_id = uuid.uuid4()
    question_id = uuid.uuid4()

    rubric = Rubric(
        id=rubric_id,
        question_id=question_id,
        title="Original Title",
        description="Original Desc",
        total_weight=1.0,
        version=1,
        is_active=True,
        grading_mode=GradingMode.AI,
        is_locked=True,  # LOCKED
        created_by=updater_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        criteria=[]
    )
    mock_rubric_repo.get_by_id.return_value = rubric
    mock_rubric_repo.save.side_effect = lambda r: r

    use_case = UpdateRubricUseCase(
        rubric_repo=mock_rubric_repo,
        criterion_repo=mock_criterion_repo,
        audit_repo=mock_audit_repo
    )

    updated_rubric = await use_case.execute(
        rubric_id=rubric_id,
        updater_id=updater_id,
        title="Updated Title"
    )

    assert updated_rubric.title == "Updated Title"
    assert updated_rubric.id != rubric_id  # NEW ID
    assert updated_rubric.version == 2  # BUMPED VERSION
    mock_rubric_repo.deactivate_all_for_question.assert_called_once_with(question_id)
    saved_log = mock_audit_repo.save.call_args[0][0]
    assert saved_log.action == AuditAction.RUBRIC_UPDATED
    assert "superseded_rubric_id" in saved_log.old_values


@pytest.mark.asyncio
async def test_delete_rubric_locked_fails(mock_rubric_repo, mock_audit_repo):
    rubric_id = uuid.uuid4()
    rubric = Rubric(
        id=rubric_id,
        question_id=uuid.uuid4(),
        title="Title",
        description="Desc",
        total_weight=1.0,
        version=1,
        is_active=True,
        grading_mode=GradingMode.AI,
        is_locked=True,  # LOCKED
        created_by=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        criteria=[]
    )
    mock_rubric_repo.get_by_id.return_value = rubric

    use_case = DeleteRubricUseCase(rubric_repo=mock_rubric_repo, audit_repo=mock_audit_repo)

    with pytest.raises(BusinessRuleViolationException) as exc_info:
        await use_case.execute(rubric_id=rubric_id, deleter_id=uuid.uuid4())

    assert "currently locked" in exc_info.value.rule
    mock_rubric_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_rubric_unlocked_success(mock_rubric_repo, mock_audit_repo):
    rubric_id = uuid.uuid4()
    rubric = Rubric(
        id=rubric_id,
        question_id=uuid.uuid4(),
        title="Title",
        description="Desc",
        total_weight=1.0,
        version=1,
        is_active=True,
        grading_mode=GradingMode.AI,
        is_locked=False,  # UNLOCKED
        created_by=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        criteria=[]
    )
    mock_rubric_repo.get_by_id.return_value = rubric
    mock_rubric_repo.delete.return_value = True

    use_case = DeleteRubricUseCase(rubric_repo=mock_rubric_repo, audit_repo=mock_audit_repo)

    success = await use_case.execute(rubric_id=rubric_id, deleter_id=uuid.uuid4())

    assert success is True
    mock_rubric_repo.delete.assert_called_once_with(rubric_id)
    mock_audit_repo.save.assert_called_once()
