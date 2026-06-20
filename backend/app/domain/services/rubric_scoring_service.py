"""
domain/services/rubric_scoring_service.py — Rubric Scoring Domain Service
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from app.domain.exceptions.domain_exception import BusinessRuleViolationException

if TYPE_CHECKING:
    from app.domain.entities.rubric import Rubric
    from app.domain.entities.rubric_criterion import RubricCriterion
    from app.domain.entities.criterion_evaluation import CriterionEvaluation


class RubricScoringService:
    """
    Handles pure domain calculations for Rubrics scoring aggregates.
    """

    @staticmethod
    def validate_rubric_weights(rubric: Rubric) -> bool:
        """
        Ensure the sum of all criteria weights matches the rubric's total weight.
        """
        if not rubric.criteria:
            return True
        actual_sum = sum(c.weight for c in rubric.criteria)
        return abs(actual_sum - rubric.total_weight) < 1e-9

    @staticmethod
    def compute_effective_marks(
        criterion: RubricCriterion,
        rubric: Rubric,
        question_max_marks: float
    ) -> float:
        """
        Calculate the absolute maximum marks allowed for this criterion based on weight.
        effective_marks = (criterion.weight / rubric.total_weight) * question_max_marks
        """
        if rubric.total_weight <= 0:
            raise BusinessRuleViolationException(rule="Rubric total weight must be greater than 0.")
        return (criterion.weight / rubric.total_weight) * question_max_marks

    @classmethod
    def aggregate_criterion_scores(
        cls,
        criterion_evaluations: list[CriterionEvaluation],
        rubric: Rubric,
        question_max_marks: float
    ) -> float:
        """
        Aggregates individual criterion scores into a single overall question score.
        Uses criteria weights normalized against the rubric's total_weight.
        """
        if not criterion_evaluations:
            return 0.0

        if rubric.total_weight <= 0:
            raise BusinessRuleViolationException(rule="Rubric total weight must be greater than 0.")

        # Create mapping of criterion_id to evaluation for quick lookup
        eval_map = {ev.rubric_criterion_id: ev for ev in criterion_evaluations}
        
        total_score = 0.0
        
        for criterion in rubric.criteria:
            evaluation = eval_map.get(criterion.id)
            if not evaluation or evaluation.final_score is None:
                # If a criterion hasn't been scored, it awards 0 marks
                continue
                
            # Score awarded is normalized by criterion weight relative to total rubric weight
            # and scaled to the question's max marks.
            # criterion.final_score is already scaled to the criterion's effective marks?
            # Wait, let's check: is the evaluation score for a criterion out of criterion.max_marks?
            # Let's check: yes, criterion.max_marks is the maximum marks for this criterion.
            # So the aggregate score is sum of final_score of each criterion, weighted?
            # Wait! If each criterion evaluation's final_score is already scaled to its max_marks,
            # we can just sum them up directly!
            # Let's verify: "question_score = sum(criterion_score * criterion.weight / total_weight) scaled to question.max_marks"
            # Or if criterion.max_marks is already (criterion.weight / total_weight) * question_max_marks,
            # then we just sum them directly.
            # Let's support both or normalize it:
            # Let's calculate the fraction scored for this criterion:
            # fraction = evaluation.final_score / criterion.max_marks
            # Then the contribution to the question is fraction * effective_marks.
            # This is mathematically the most general and robust way!
            effective_max = cls.compute_effective_marks(criterion, rubric, question_max_marks)
            
            # Prevent DivisionByZero if criterion max_marks is 0 (though invariant prevents it)
            crit_max = criterion.max_marks if criterion.max_marks > 0 else 1.0
            fraction = evaluation.final_score / crit_max
            
            # Ensure fraction is bounded [0, 1]
            fraction = max(0.0, min(1.0, fraction))
            
            total_score += fraction * effective_max

        return round(total_score, 2)
