"""
infrastructure/ai/evaluation_explanation_service.py — Evaluation Explanation Service
"""

from __future__ import annotations


class EvaluationExplanationService:
    """
    Generates structured, explainable feedback on student answers.
    """

    def generate_explanation(
        self,
        similarity_score: float,
        matched_keywords: list[str],
        missing_keywords: list[str],
        criterion_results: list[dict] | None,
        max_marks: float,
        final_score: float,
        applied_weights: dict
    ) -> dict:
        """
        Synthesizes AI scoring into structured strengths, weaknesses,
        missing topics, improvement suggestions, and scoring reasoning.
        """
        # 1. Strengths
        strengths = []
        if similarity_score >= 0.75:
            strengths.append("Demonstrated excellent overall conceptual similarity to the model answer.")
        elif similarity_score >= 0.50:
            strengths.append("Captured basic conceptual structures matching the model answer.")
        else:
            strengths.append("Shows basic attempt, but the explanation deviates from the expected conceptual framework.")

        if matched_keywords:
            strengths.append(f"Successfully included critical keywords/phrases: {', '.join(matched_keywords[:5])}.")

        # Check criterion level strengths
        if criterion_results:
            high_scoring_criteria = [cr["criterion_name"] for cr in criterion_results if (cr["awarded_marks"] / cr["max_marks"]) >= 0.75 if cr["max_marks"] > 0]
            if high_scoring_criteria:
                strengths.append(f"Exhibited high performance on rubric dimensions: {', '.join(high_scoring_criteria)}.")

        # 2. Weaknesses
        weaknesses = []
        if similarity_score < 0.50:
            weaknesses.append("Significant divergence from expected model answer definitions or context.")
        elif similarity_score < 0.75:
            weaknesses.append("Conceptual elaboration is somewhat shallow or missing minor details.")

        if missing_keywords:
            weaknesses.append(f"Omitted key technical terms: {', '.join(missing_keywords[:5])}.")

        # Check criterion level weaknesses
        if criterion_results:
            low_scoring_criteria = [cr["criterion_name"] for cr in criterion_results if (cr["awarded_marks"] / cr["max_marks"]) < 0.50 if cr["max_marks"] > 0]
            if low_scoring_criteria:
                weaknesses.append(f"Needs improvement on rubric dimensions: {', '.join(low_scoring_criteria)}.")

        # 3. Missing Topics
        missing_topics = missing_keywords

        # 4. Improvement Suggestions
        suggestions = []
        if missing_keywords:
            suggestions.append(f"Incorporate missing core concepts like: {', '.join(missing_keywords[:3])}.")
        if similarity_score < 0.70:
            suggestions.append("Structure the explanation more clearly, ensuring direct correspondence to the model answer definition.")
        if criterion_results:
            remediating_criteria = [cr["criterion_name"] for cr in criterion_results if (cr["awarded_marks"] / cr["max_marks"]) < 0.60 if cr["max_marks"] > 0]
            if remediating_criteria:
                suggestions.append(f"Focus revisions on strengthening your explanation for {', '.join(remediating_criteria)}.")
        
        if not suggestions:
            suggestions.append("Maintain this high level of technical rigor in future assessments.")

        # 5. Scoring Reasoning
        sem_w = applied_weights.get("semantic_weight", 0.0) * 100
        kw_w = applied_weights.get("keyword_weight", 0.0) * 100
        rub_w = applied_weights.get("rubric_weight", 0.0) * 100

        reasoning = (
            f"The final score of {final_score} / {max_marks} was calculated via weighted aggregation: "
            f"Semantic similarity match contributed {sem_w:.1f}% to the score, technical keyword coverage contributed {kw_w:.1f}%, "
            f"and Rubric criteria criteria-specific performance contributed {rub_w:.1f}%."
        )

        return {
            "strengths": " ".join(strengths),
            "weaknesses": " ".join(weaknesses) if weaknesses else "No significant conceptual weaknesses detected.",
            "missing_topics": missing_topics,
            "improvement_suggestions": " ".join(suggestions),
            "scoring_reasoning": reasoning
        }
