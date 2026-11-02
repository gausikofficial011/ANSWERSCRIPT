"""
infrastructure/ai/score_aggregation_service.py — Score Aggregation Engine
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ScoreAggregationService:
    """
    Aggregates Semantic, Keyword, and Rubric scores using configurable weights.
    """

    def aggregate_score(
        self,
        similarity_score: float,
        keyword_match_score: float,
        rubric_score: float | None,
        max_marks: float,
        exam_scoring_config: dict | None = None
    ) -> dict:
        """
        Combines evaluation scores using weights defined in exam_scoring_config.
        
        Default weights:
          - Rubric questions: Semantic: 20%, Keywords: 30%, Rubric: 50%
          - Non-rubric questions: Semantic: 40%, Keywords: 60%
        """
        # Load weights from config or use defaults
        config = exam_scoring_config or {}
        
        if rubric_score is not None:
            default_sem_w = 0.20
            default_kw_w = 0.30
            default_rub_w = 0.50
        else:
            default_sem_w = 0.40
            default_kw_w = 0.60
            default_rub_w = 0.00

        sem_w = config.get("semantic_weight", default_sem_w)
        kw_w = config.get("keyword_weight", default_kw_w)
        rub_w = config.get("rubric_weight", default_rub_w)
        
        # Normalize weights to ensure they sum to 1.0
        total_w = sem_w + kw_w + rub_w
        if total_w > 0:
            sem_w /= total_w
            kw_w /= total_w
            rub_w /= total_w
        else:
            sem_w = default_sem_w
            kw_w = default_kw_w
            rub_w = default_rub_w

        # Configurable Keyword Threshold Gating (Soft Gating)
        gating_threshold = config.get("keyword_gating_threshold", 0.20)
        if gating_threshold > 0.0:
            raw_mult = keyword_match_score / gating_threshold
            multiplier = max(0.25, min(1.0, raw_mult))
        else:
            multiplier = 1.0

        raw_semantic_component = similarity_score * max_marks
        semantic_component = raw_semantic_component * multiplier
        keyword_component = keyword_match_score * max_marks
        
        if rubric_score is None:
            # No rubric active, redistribute rubric weight to Semantic & Keywords
            denom = sem_w + kw_w
            if denom > 0:
                adj_sem_w = sem_w / denom
                adj_kw_w = kw_w / denom
            else:
                adj_sem_w = 0.40
                adj_kw_w = 0.60
                
            final_score = (adj_sem_w * semantic_component) + (adj_kw_w * keyword_component)
            rubric_score_effective = 0.0
        else:
            # Rubric active, compute full weighted sum
            final_score = (sem_w * semantic_component) + (kw_w * keyword_component) + (rub_w * rubric_score)
            rubric_score_effective = rubric_score

        # Bound final score to [0.0, max_marks]
        final_score = max(0.0, min(float(max_marks), round(final_score, 2)))
        
        percentage = (final_score / max_marks) * 100.0 if max_marks > 0 else 0.0
        normalized_score = final_score / max_marks if max_marks > 0 else 0.0

        return {
            "final_score": final_score,
            "percentage": round(percentage, 2),
            "normalized_score": round(normalized_score, 4),
            "semantic_component_score": round(semantic_component, 2),
            "keyword_component_score": round(keyword_component, 2),
            "rubric_component_score": round(rubric_score_effective, 2),
            "applied_weights": {
                "semantic_weight": round(sem_w if rubric_score is not None else sem_w / (sem_w + kw_w), 4),
                "keyword_weight": round(kw_w if rubric_score is not None else kw_w / (sem_w + kw_w), 4),
                "rubric_weight": round(rub_w if rubric_score is not None else 0.0, 4)
            }
        }
