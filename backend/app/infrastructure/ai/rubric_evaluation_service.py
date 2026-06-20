"""
infrastructure/ai/rubric_evaluation_service.py — Rubric-Based Evaluation Service
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.infrastructure.ai.semantic_similarity_service import SemanticSimilarityService
from app.infrastructure.ai.keyword_evaluation_service import KeywordEvaluationService

if TYPE_CHECKING:
    from app.domain.entities.rubric import Rubric
    from app.domain.entities.criterion_evaluation import CriterionEvaluation


class RubricEvaluationService:
    """
    Evaluates student answers against structured Rubrics at the criterion level.
    """

    def __init__(
        self,
        semantic_service: SemanticSimilarityService | None = None,
        keyword_service: KeywordEvaluationService | None = None,
    ) -> None:
        self.semantic_service = semantic_service or SemanticSimilarityService()
        self.keyword_service = keyword_service or KeywordEvaluationService()

    def evaluate_rubric(
        self,
        student_answer: str,
        rubric: Rubric,
        model_answer: str,
        question_max_marks: float,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> list[dict]:
        """
        Evaluates student answer against all criteria of a Rubric.
        
        Returns:
            list[dict]: List of criterion evaluation details including awarded_marks, feedback, confidence.
        """
        results = []

        for criterion in rubric.criteria:
            # 1. Compute semantic similarity component
            # Compare student answer against the model answer (or the criterion description if model answer is empty)
            comparison_text = model_answer if model_answer.strip() else (criterion.criterion_description or "")
            sim_score = self.semantic_service.compute_similarity(student_answer, comparison_text)

            # 2. Compute keyword matching component for criterion-specific expected keywords
            keyword_results = self.keyword_service.evaluate_keywords(
                student_answer,
                criterion.expected_keywords
            )
            kw_score = keyword_results["keyword_score"]

            # 3. Combine scores
            # Use weights (defaults are 0.7 semantic, 0.3 keywords)
            combined_score = (sim_score * semantic_weight) + (kw_score * keyword_weight)
            
            # Compute criterion maximum marks relative to rubric total weight
            effective_max_marks = (criterion.weight / rubric.total_weight) * question_max_marks if rubric.total_weight > 0 else criterion.max_marks
            
            awarded_marks = round(combined_score * effective_max_marks, 2)
            
            # 4. Generate feedback specific to this criterion
            matched_kws = keyword_results["matched_keywords"]
            missing_kws = keyword_results["missing_keywords"]
            
            feedback_parts = [f"Criterion '{criterion.criterion_name}':"]
            if sim_score >= 0.75:
                feedback_parts.append("Concept is explained with high accuracy.")
            elif sim_score >= 0.50:
                feedback_parts.append("Concept is partially explained but lacks detail.")
            else:
                feedback_parts.append("Explanation deviates from expected conceptual model.")

            if matched_kws:
                feedback_parts.append(f"Successfully matched: {', '.join(matched_kws)}.")
            if missing_kws:
                feedback_parts.append(f"Missing expected terms: {', '.join(missing_kws)}.")
                
            criterion_feedback = " ".join(feedback_parts)
            
            # 5. Calculate per-criterion confidence score
            # Confidence decreases if semantic score and keyword score differ widely
            agreement = 1.0 - abs(sim_score - kw_score)
            criterion_confidence = round(0.6 * sim_score + 0.4 * agreement, 2)

            results.append({
                "rubric_criterion_id": criterion.id,
                "criterion_name": criterion.criterion_name,
                "max_marks": effective_max_marks,
                "awarded_marks": awarded_marks,
                "ai_semantic_score": sim_score,
                "ai_keyword_score": kw_score,
                "ai_score": awarded_marks,
                "ai_feedback": criterion_feedback,
                "confidence": criterion_confidence
            })

        return results
