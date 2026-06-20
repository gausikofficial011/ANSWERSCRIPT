"""
tests/unit/infrastructure/test_evaluation_services.py — Unit Tests for AI Evaluation Services
"""

from __future__ import annotations

import pytest
import uuid
from unittest.mock import MagicMock

from app.infrastructure.ai.semantic_similarity_service import SemanticSimilarityService
from app.infrastructure.ai.keyword_evaluation_service import KeywordEvaluationService
from app.infrastructure.ai.rubric_evaluation_service import RubricEvaluationService
from app.infrastructure.ai.score_aggregation_service import ScoreAggregationService
from app.infrastructure.ai.evaluation_explanation_service import EvaluationExplanationService
from app.domain.entities.rubric import Rubric
from app.domain.entities.rubric_criterion import RubricCriterion
from app.core.constants import GradingMode


@pytest.fixture
def mock_embedder():
    embedder = MagicMock()
    # Mock return values for embeddings
    embedder.encode.side_effect = lambda text: [1.0, 0.0, 0.0] if "student" in text else [0.8, 0.6, 0.0]
    return embedder


def test_semantic_similarity_service(mock_embedder):
    service = SemanticSimilarityService(embedder=mock_embedder)
    
    # Test identical direction clamping/scores
    # If vec_student is [1, 0, 0] and vec_model is [0.8, 0.6, 0], similarity is 0.8
    score = service.compute_similarity("student answer", "model answer")
    assert 0.0 <= score <= 1.0
    assert abs(score - 0.8) < 1e-4

    # Test empty string edge cases
    assert service.compute_similarity("", "model answer") == 0.0
    assert service.compute_similarity("student", "") == 0.0


def test_keyword_evaluation_service():
    service = KeywordEvaluationService()
    
    student = "We are using Sentence Transformers for AI evaluation."
    keywords = ["Sentence Transformers", "AI", "unrelated keyword"]
    
    results = service.evaluate_keywords(student, keywords)
    
    assert results["keyword_score"] == 2.0 / 3.0
    assert "Sentence Transformers" in results["matched_keywords"]
    assert "AI" in results["matched_keywords"]
    assert "unrelated keyword" in results["missing_keywords"]
    assert results["keyword_coverage_percentage"] == pytest.approx(66.666, 0.01)

    # Empty expected keywords edge case
    empty_results = service.evaluate_keywords(student, [])
    assert empty_results["keyword_score"] == 1.0
    assert empty_results["matched_keywords"] == []


def test_rubric_evaluation_service(mock_embedder):
    rubric_id = uuid.uuid4()
    c1 = RubricCriterion(
        id=uuid.uuid4(),
        rubric_id=rubric_id,
        criterion_name="Concept Accuracy",
        weight=0.5,
        max_marks=5.0,
        order_index=0,
        expected_keywords=["concept"],
        created_at=MagicMock(),
        updated_at=MagicMock()
    )
    c2 = RubricCriterion(
        id=uuid.uuid4(),
        rubric_id=rubric_id,
        criterion_name="Clarity",
        weight=0.5,
        max_marks=5.0,
        order_index=1,
        expected_keywords=["clarity"],
        created_at=MagicMock(),
        updated_at=MagicMock()
    )
    rubric = Rubric(
        id=rubric_id,
        question_id=uuid.uuid4(),
        title="Sample Rubric",
        total_weight=1.0,
        version=1,
        is_active=True,
        grading_mode=GradingMode.AI,
        created_by=uuid.uuid4(),
        created_at=MagicMock(),
        updated_at=MagicMock(),
        criteria=[c1, c2]
    )

    semantic_service = SemanticSimilarityService(embedder=mock_embedder)
    keyword_service = KeywordEvaluationService()
    service = RubricEvaluationService(semantic_service, keyword_service)
    
    results = service.evaluate_rubric(
        student_answer="This concept shows clear explanation.",
        rubric=rubric,
        model_answer="concept clarity model answer",
        question_max_marks=10.0
    )
    
    assert len(results) == 2
    assert results[0]["criterion_name"] == "Concept Accuracy"
    assert results[0]["max_marks"] == 5.0
    assert results[0]["awarded_marks"] >= 0.0
    assert results[1]["criterion_name"] == "Clarity"


def test_score_aggregation_service():
    service = ScoreAggregationService()
    
    # 1. Rubric active
    results = service.aggregate_score(
        similarity_score=0.8,
        keyword_match_score=0.5,
        rubric_score=8.0,
        max_marks=10.0,
        exam_scoring_config={
            "semantic_weight": 0.40,
            "keyword_weight": 0.20,
            "rubric_weight": 0.40
        }
    )
    
    # semantic contribution = 0.8 * 10 * 0.4 = 3.2
    # keyword contribution = 0.5 * 10 * 0.2 = 1.0
    # rubric contribution = 8.0 * 0.4 = 3.2
    # total = 7.4
    assert results["final_score"] == 7.4
    assert results["percentage"] == 74.0

    # 2. No Rubric (weights redistributed proportionally)
    results_no_rubric = service.aggregate_score(
        similarity_score=0.8,
        keyword_match_score=0.5,
        rubric_score=None,
        max_marks=10.0,
        exam_scoring_config={
            "semantic_weight": 0.40,
            "keyword_weight": 0.20,
            "rubric_weight": 0.40
        }
    )
    # redistributed: semantic_weight = 0.4 / 0.6 = 2/3, keyword_weight = 0.2 / 0.6 = 1/3
    # score = (2/3 * 8.0) + (1/3 * 5.0) = 5.33 + 1.67 = 7.0
    assert results_no_rubric["final_score"] == 7.0


def test_evaluation_explanation_service():
    service = EvaluationExplanationService()
    
    explanation = service.generate_explanation(
        similarity_score=0.8,
        matched_keywords=["concept"],
        missing_keywords=["depth"],
        criterion_results=None,
        max_marks=10.0,
        final_score=7.0,
        applied_weights={
            "semantic_weight": 0.6,
            "keyword_weight": 0.4,
            "rubric_weight": 0.0
        }
    )
    
    assert "strengths" in explanation
    assert "weaknesses" in explanation
    assert "concept" in explanation["strengths"]
    assert "depth" in explanation["weaknesses"]
    assert explanation["missing_topics"] == ["depth"]
    assert "scoring_reasoning" in explanation
