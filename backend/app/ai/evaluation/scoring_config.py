"""
ai/evaluation/scoring_config.py — Per-Exam Evaluation Scoring Configuration

Encapsulates all configurable scoring parameters for a single exam.
Teachers can set these values per exam (user requirement: configurable weights).

Stored as JSONB in the exams table under the `scoring_config` column.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from app.core.constants import (
    AI_DEFAULT_SEMANTIC_WEIGHT,
    AI_DEFAULT_KEYWORD_WEIGHT,
    PLAGIARISM_DEFAULT_THRESHOLD,
)


@dataclass
class ScoringConfig:
    """
    Per-exam AI scoring configuration.

    Attributes:
        semantic_weight:         Weight given to semantic similarity (0.0–1.0).
        keyword_weight:          Weight given to keyword matching (0.0–1.0).
                                 semantic_weight + keyword_weight must equal 1.0.
        plagiarism_threshold:    Similarity percentage above which sheets are
                                 flagged as plagiarised (0.0–1.0).
        min_answer_length_chars: Minimum answer length before a partial-answer
                                 penalty is applied (0 = disabled).
        enable_keyword_penalty:  If True, missing critical keywords reduce score
                                 even with high semantic similarity.
        question_type_overrides: Per-question-type weight overrides.
                                 Keys are QuestionType enum values.
    """

    semantic_weight: float = AI_DEFAULT_SEMANTIC_WEIGHT
    keyword_weight: float = AI_DEFAULT_KEYWORD_WEIGHT
    plagiarism_threshold: float = PLAGIARISM_DEFAULT_THRESHOLD
    min_answer_length_chars: int = 0
    enable_keyword_penalty: bool = False
    question_type_overrides: dict[str, dict[str, float]] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        total = round(self.semantic_weight + self.keyword_weight, 10)
        if abs(total - 1.0) > 1e-9:
            raise ValueError(
                f"semantic_weight ({self.semantic_weight}) + keyword_weight "
                f"({self.keyword_weight}) must equal 1.0, got {total}."
            )
        if not (0.0 <= self.semantic_weight <= 1.0):
            raise ValueError("semantic_weight must be between 0.0 and 1.0.")
        if not (0.0 < self.plagiarism_threshold <= 1.0):
            raise ValueError("plagiarism_threshold must be between 0.0 and 1.0.")

    @classmethod
    def default(cls) -> "ScoringConfig":
        """Return the system default scoring configuration."""
        return cls()

    def weights_for_question_type(self, question_type: str) -> dict[str, float]:
        """
        Return effective weights for a specific question type.
        Falls back to exam-level defaults if no override exists.
        """
        if question_type in self.question_type_overrides:
            return self.question_type_overrides[question_type]
        return {
            "semantic_weight": self.semantic_weight,
            "keyword_weight": self.keyword_weight,
        }

    def to_dict(self) -> dict:
        """Serialize to dict for JSONB storage in the database."""
        return {
            "semantic_weight": self.semantic_weight,
            "keyword_weight": self.keyword_weight,
            "plagiarism_threshold": self.plagiarism_threshold,
            "min_answer_length_chars": self.min_answer_length_chars,
            "enable_keyword_penalty": self.enable_keyword_penalty,
            "question_type_overrides": self.question_type_overrides,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScoringConfig":
        """Deserialize from JSONB database value."""
        return cls(**data)
