"""
tests/unit/application/test_evaluation_use_cases.py — Unit Tests for AI Evaluation Use Cases
"""

from __future__ import annotations

import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.domain.entities.evaluation import Evaluation
from app.domain.entities.criterion_evaluation import CriterionEvaluation
from app.domain.entities.question_mapping import QuestionMapping
from app.domain.entities.question import Question
from app.domain.entities.model_answer import ModelAnswer
from app.domain.entities.rubric import Rubric
from app.domain.entities.rubric_criterion import RubricCriterion
from app.domain.entities.answer_sheet import AnswerSheet

from app.application.use_cases.evaluations.evaluate_answer_use_case import EvaluateAnswerUseCase
from app.application.use_cases.evaluations.evaluate_answer_sheet_use_case import EvaluateAnswerSheetUseCase
from app.application.use_cases.evaluations.verify_evaluation_use_case import VerifyEvaluationUseCase
from app.application.use_cases.evaluations.re_evaluate_use_case import ReEvaluateUseCase

from app.core.constants import AnswerSheetStatus, GradingMode


@pytest.fixture
def mock_repos():
    return {
        "evaluation_repo": AsyncMock(),
        "revision_repo": AsyncMock(),
        "criterion_eval_repo": AsyncMock(),
        "question_mapping_repo": AsyncMock(),
        "question_repo": AsyncMock(),
        "model_answer_repo": AsyncMock(),
        "rubric_repo": AsyncMock(),
        "answer_sheet_repo": AsyncMock(),
        "audit_repo": AsyncMock()
    }


@pytest.mark.asyncio
async def test_evaluate_answer_use_case_not_attempted(mock_repos):
    use_case = EvaluateAnswerUseCase(
        evaluation_repo=mock_repos["evaluation_repo"],
        revision_repo=mock_repos["revision_repo"],
        criterion_eval_repo=mock_repos["criterion_eval_repo"],
        question_mapping_repo=mock_repos["question_mapping_repo"],
        question_repo=mock_repos["question_repo"],
        model_answer_repo=mock_repos["model_answer_repo"],
        rubric_repo=mock_repos["rubric_repo"],
        audit_repo=mock_repos["audit_repo"]
    )

    sheet_id = uuid.uuid4()
    mapping_id = uuid.uuid4()
    question_id = uuid.uuid4()
    
    mapping = QuestionMapping(
        id=mapping_id,
        answer_sheet_id=sheet_id,
        question_id=question_id,
        detected_question_number=1,
        detected_question_label="Q1",
        extracted_answer_text="",
        start_page=1,
        end_page=1,
        mapping_confidence=0.9,
        status="NOT_ATTEMPTED"
    )
    mock_repos["question_mapping_repo"].get_by_id.return_value = mapping
    
    question = Question(
        id=question_id,
        exam_id=uuid.uuid4(),
        question_number=1,
        marks=10,
        question_text="text",
        question_type="descriptive",
        created_by=uuid.uuid4()
    )
    mock_repos["question_repo"].get_by_id.return_value = question
    
    model_ans = ModelAnswer(id=uuid.uuid4(), question_id=question_id, answer_text="model text", keywords=["model"], created_by=uuid.uuid4())
    mock_repos["model_answer_repo"].get_by_question_id.return_value = model_ans
    
    mock_repos["rubric_repo"].get_active_by_question_id.return_value = None
    mock_repos["evaluation_repo"].get_by_question_id.return_value = None
    mock_repos["evaluation_repo"].save.side_effect = lambda e: e

    eval_result = await use_case.execute(sheet_id, mapping_id)
    
    assert eval_result.ai_score == 0.0
    assert eval_result.similarity_score == 0.0
    assert eval_result.keyword_match_score == 0.0
    assert eval_result.evaluation_confidence == 1.0
    assert eval_result.explanation["weaknesses"] == "Question not attempted by the student."
    
    mock_repos["evaluation_repo"].save.assert_called_once()


@pytest.mark.asyncio
async def test_evaluate_answer_sheet_use_case_low_confidence(mock_repos):
    # Setup mock EvaluateAnswerUseCase
    mock_eval_use_case = MagicMock()
    
    use_case = EvaluateAnswerSheetUseCase(
        answer_sheet_repo=mock_repos["answer_sheet_repo"],
        question_mapping_repo=mock_repos["question_mapping_repo"],
        audit_repo=mock_repos["audit_repo"],
        evaluate_answer_use_case=mock_eval_use_case
    )
    
    sheet_id = uuid.uuid4()
    sheet = AnswerSheet(
        id=sheet_id,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="ans.pdf",
        stored_filename="ans_stored.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.UPLOADED,
        processing_status=AnswerSheetStatus.UPLOADED
    )
    mock_repos["answer_sheet_repo"].get_by_id.return_value = sheet
    
    mapping1 = QuestionMapping(
        id=uuid.uuid4(),
        answer_sheet_id=sheet_id,
        question_id=uuid.uuid4(),
        detected_question_number=1,
        detected_question_label="Q1",
        extracted_answer_text="Ans 1",
        start_page=1,
        end_page=1,
        mapping_confidence=0.8,
        status="MAPPED"
    )
    mock_repos["question_mapping_repo"].list_by_answer_sheet_id.return_value = [mapping1]
    
    # Mock evaluation with low confidence (0.45)
    eval_result = Evaluation(
        id=uuid.uuid4(),
        answer_sheet_id=sheet_id,
        question_mapping_id=mapping1.id,
        question_id=mapping1.question_id,
        model_answer_id=uuid.uuid4(),
        max_marks=10,
        ai_score=5.0,
        similarity_score=0.5,
        keyword_match_score=0.5,
        evaluation_confidence=0.45  # < 0.50
    )
    mock_eval_use_case.execute = AsyncMock(return_value=eval_result)
    mock_repos["answer_sheet_repo"].save.side_effect = lambda s: s

    res = await use_case.execute(sheet_id)
    
    # Should flag requires_review as True and set status to TEACHER_REVIEW_PENDING
    assert res["requires_review"] is True
    assert res["status"] == AnswerSheetStatus.TEACHER_REVIEW_PENDING
    assert sheet.status == AnswerSheetStatus.TEACHER_REVIEW_PENDING


@pytest.mark.asyncio
async def test_verify_evaluation_use_case_complete_override(mock_repos):
    use_case = VerifyEvaluationUseCase(
        evaluation_repo=mock_repos["evaluation_repo"],
        revision_repo=mock_repos["revision_repo"],
        criterion_eval_repo=mock_repos["criterion_eval_repo"],
        rubric_repo=mock_repos["rubric_repo"],
        answer_sheet_repo=mock_repos["answer_sheet_repo"],
        audit_repo=mock_repos["audit_repo"]
    )
    
    eval_id = uuid.uuid4()
    evaluation = Evaluation(
        id=eval_id,
        answer_sheet_id=uuid.uuid4(),
        question_mapping_id=uuid.uuid4(),
        question_id=uuid.uuid4(),
        model_answer_id=uuid.uuid4(),
        max_marks=10,
        ai_score=4.0,
        similarity_score=0.4,
        keyword_match_score=0.4,
        is_verified=False
    )
    mock_repos["evaluation_repo"].get_by_id.return_value = evaluation
    mock_repos["revision_repo"].get_next_revision_number.return_value = 1
    mock_repos["evaluation_repo"].save.side_effect = lambda e: e
    
    sheet = AnswerSheet(
        id=evaluation.answer_sheet_id,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="ans.pdf",
        stored_filename="ans_stored.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.EVALUATION_COMPLETED,
        processing_status=AnswerSheetStatus.EVALUATION_COMPLETED
    )
    mock_repos["answer_sheet_repo"].get_by_id.return_value = sheet
    mock_repos["evaluation_repo"].get_by_answer_sheet_id.return_value = [evaluation]

    verifier_id = uuid.uuid4()
    res = await use_case.execute(
        evaluation_id=eval_id,
        teacher_score=7.5,
        teacher_feedback="Much better explanation.",
        verifier_id=verifier_id,
        reason="Lenient spelling"
    )
    
    assert res.is_verified is True
    assert res.teacher_score == 7.5
    assert res.final_score == 7.5
    assert res.verified_by == verifier_id
    
    # Check that revisions were saved
    mock_repos["revision_repo"].save.assert_called_once()
    # Check that AnswerSheet transitioned to VERIFIED since all sheet evaluations (only 1) are verified
    assert sheet.status == AnswerSheetStatus.VERIFIED
