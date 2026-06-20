"""
domain/value_objects/score.py — Score Value Object

Represents a numeric evaluation score bounded by a maximum marks value.
Enforces domain invariants: score cannot be negative or exceed maximum.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    """
    Immutable score value object.

    Invariants:
      - value >= 0.0
      - value <= max_marks
      - max_marks > 0

    Usage:
      score = Score(value=7.5, max_marks=10)
      score.percentage  → 75.0
    """

    value: float
    max_marks: int

    def __post_init__(self) -> None:
        if self.max_marks <= 0:
            raise ValueError("max_marks must be a positive integer.")
        if self.value < 0.0:
            raise ValueError("Score value cannot be negative.")
        if self.value > self.max_marks:
            raise ValueError(
                f"Score value {self.value} exceeds max_marks {self.max_marks}."
            )

    @property
    def percentage(self) -> float:
        """Return percentage representation, rounded to 2 decimal places."""
        return round((self.value / self.max_marks) * 100, 2)

    @property
    def is_zero(self) -> bool:
        return self.value == 0.0

    @property
    def is_full(self) -> bool:
        return self.value == float(self.max_marks)

    def __str__(self) -> str:
        return f"{self.value}/{self.max_marks}"

    def __repr__(self) -> str:
        return f"Score(value={self.value}, max_marks={self.max_marks})"


@dataclass(frozen=True)
class SimilarityScore:
    """
    Immutable similarity score in range [0.0, 1.0].

    Used for both AI evaluation similarity and plagiarism detection.

    Invariants:
      - value is in [0.0, 1.0]
    """

    value: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.value <= 1.0):
            raise ValueError(
                f"SimilarityScore must be between 0.0 and 1.0, got {self.value}."
            )

    @property
    def as_percentage(self) -> float:
        return round(self.value * 100, 2)

    def exceeds_threshold(self, threshold: float) -> bool:
        return self.value >= threshold

    def __str__(self) -> str:
        return f"{self.as_percentage}%"

    def __repr__(self) -> str:
        return f"SimilarityScore({self.value})"
