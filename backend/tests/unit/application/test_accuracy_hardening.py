import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from app.infrastructure.ai.score_aggregation_service import ScoreAggregationService
from app.application.use_cases.evaluations.evaluate_answer_use_case import EvaluateAnswerUseCase
from app.domain.entities.question_mapping import QuestionMapping
from app.domain.entities.evaluation import Evaluation


def test_score_aggregation_gating_and_weights():
    service = ScoreAggregationService()

    # 1. Test aggregation weights WITHOUT rubric
    # Expect 40% Semantic, 60% Keyword
    # Gating threshold = 0.20
    # Case A: Keyword match score is 0.0 (below 0.20 threshold). Semantic score should be fully gated to 0.0.
    res_a = service.aggregate_score(
        similarity_score=0.80, # 8.0 out of 10.0 max
        keyword_match_score=0.0,
        rubric_score=None,
        max_marks=10.0
    )
    # Expected final score under soft gating: (0.40 * 8.0 * 0.25) + (0.60 * 0.0) = 0.80
    assert res_a["final_score"] == 0.80
    assert res_a["applied_weights"]["semantic_weight"] == 0.40
    assert res_a["applied_weights"]["keyword_weight"] == 0.60

    # Case B: Keyword match score is 0.10 (below 0.20 threshold). Semantic score should be gated by 0.10 / 0.20 = 0.50.
    res_b = service.aggregate_score(
        similarity_score=0.80, # 8.0 out of 10.0 max
        keyword_match_score=0.10,
        rubric_score=None,
        max_marks=10.0
    )
    # Expected: (0.40 * 8.0 * 0.5) + (0.60 * 1.0) = 1.6 + 0.6 = 2.2
    assert res_b["final_score"] == 2.20

    # Case C: Keyword match score is 0.20 (at threshold). No attenuation.
    res_c = service.aggregate_score(
        similarity_score=0.80,
        keyword_match_score=0.20,
        rubric_score=None,
        max_marks=10.0
    )
    # Expected: (0.40 * 8.0) + (0.60 * 2.0) = 3.2 + 1.2 = 4.4
    assert res_c["final_score"] == 4.40

    # 2. Test aggregation weights WITH rubric
    # Expect 20% Semantic, 30% Keyword, 50% Rubric
    # Case D: No rubric gating attenuation (keyword_match_score = 0.50)
    res_d = service.aggregate_score(
        similarity_score=0.90,
        keyword_match_score=0.50,
        rubric_score=8.0,
        max_marks=10.0
    )
    # Expected: (0.20 * 9.0) + (0.30 * 5.0) + (0.50 * 8.0) = 1.8 + 1.5 + 4.0 = 7.3
    assert res_d["final_score"] == 7.30
    assert res_d["applied_weights"]["semantic_weight"] == 0.20
    assert res_d["applied_weights"]["keyword_weight"] == 0.30
    assert res_d["applied_weights"]["rubric_weight"] == 0.50


@pytest.mark.asyncio
async def test_evaluate_answer_use_case_confidence_flagging():
    # Setup mocks
    evaluation_repo = MagicMock()
    evaluation_repo.get_by_question_id = AsyncMock(return_value=None)
    evaluation_repo.save = AsyncMock(side_effect=lambda e: e)
    
    revision_repo = MagicMock()
    criterion_eval_repo = MagicMock()
    
    question_mapping_repo = MagicMock()
    question = MagicMock()
    question.marks = 10.0
    question_repo = MagicMock()
    question_repo.get_by_id = AsyncMock(return_value=question)
    
    model_answer = MagicMock()
    model_answer.id = uuid.uuid4()
    model_answer.answer_text = "correct answer"
    model_answer.keywords = ["correct", "answer"]
    model_answer_repo = MagicMock()
    model_answer_repo.get_by_question_id = AsyncMock(return_value=model_answer)
    
    rubric_repo = MagicMock()
    rubric_repo.get_active_by_question_id = AsyncMock(return_value=None)
    
    audit_repo = MagicMock()
    audit_repo.save = AsyncMock()

    semantic_service = MagicMock()
    semantic_service.compute_similarity = MagicMock(return_value=0.90)

    keyword_service = MagicMock()
    keyword_service.evaluate_keywords = MagicMock(return_value={
        "keyword_score": 0.0, # Divergence is 0.90 - 0.0 = 0.90
        "matched_keywords": [],
        "missing_keywords": ["correct", "answer"]
    })

    aggregation_service = ScoreAggregationService()
    explanation_service = MagicMock()
    explanation_service.generate_explanation = MagicMock(return_value={"strengths": "Feedback strengths"})

    use_case = EvaluateAnswerUseCase(
        evaluation_repo=evaluation_repo,
        revision_repo=revision_repo,
        criterion_eval_repo=criterion_eval_repo,
        question_mapping_repo=question_mapping_repo,
        question_repo=question_repo,
        model_answer_repo=model_answer_repo,
        rubric_repo=rubric_repo,
        audit_repo=audit_repo,
        semantic_service=semantic_service,
        keyword_service=keyword_service,
        aggregation_service=aggregation_service,
        explanation_service=explanation_service
    )

    # Case A: Low mapping (OCR) confidence = 0.50, high semantic-keyword divergence (0.90 vs 0.0)
    mapping = QuestionMapping(
        answer_sheet_id=uuid.uuid4(),
        question_id=uuid.uuid4(),
        detected_question_number=1,
        detected_question_label="Q1",
        extracted_answer_text="poor text",
        start_page=1,
        end_page=1,
        mapping_confidence=0.50, # Low OCR
        status="ATTEMPTED"
    )
    question_mapping_repo.get_by_id = AsyncMock(return_value=mapping)

    eval_a = await use_case.execute(
        answer_sheet_id=mapping.answer_sheet_id,
        question_mapping_id=mapping.id
    )

    # Expected confidence components:
    # OCR confidence = 0.50
    # Divergence = abs(0.90 - 0.0) = 0.90
    # std_dev = 0.0 (no rubric)
    # score = 0.5 * 0.50 + 0.3 * (1.0 - 0.90) - 0.2 * 0.0 = 0.25 + 0.03 = 0.28
    assert eval_a.confidence_score == 0.28
    assert eval_a.low_confidence_flag is True

    # Case B: High mapping confidence = 1.0, low divergence (1.0 similarity vs 1.0 keyword match)
    semantic_service.compute_similarity = MagicMock(return_value=1.0)
    keyword_service.evaluate_keywords = MagicMock(return_value={
        "keyword_score": 1.0, # Divergence = 0.0
        "matched_keywords": ["correct"],
        "missing_keywords": []
    })
    mapping.mapping_confidence = 1.0

    eval_b = await use_case.execute(
        answer_sheet_id=mapping.answer_sheet_id,
        question_mapping_id=mapping.id
    )

    # Expected confidence:
    # OCR confidence = 1.0
    # Divergence = 0.0
    # score = 0.5 * 1.0 + 0.3 * 1.0 = 0.50 + 0.30 = 0.80
    assert eval_b.confidence_score == 0.80
    assert eval_b.low_confidence_flag is False
