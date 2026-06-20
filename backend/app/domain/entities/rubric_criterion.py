"""
domain/entities/rubric_criterion.py — RubricCriterion Entity

A RubricCriterion defines one scoring dimension within a Rubric.
Teachers define the criterion name, description, weight, max_marks,
and expected keywords for AI matching.

Invariants:
  - weight must be in (0.0, 1.0]
  - max_marks must be > 0
  - expected_keywords length in [0, 20]
  - order_index >= 0
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RubricCriterion:
    """
    A single marking criterion within a Rubric.

    Attributes:
        id:                    UUID primary key.
        rubric_id:             Parent rubric UUID.
        criterion_name:        Short label (e.g., "Concept Clarity").
        criterion_description: Detailed description of what this criterion assesses.
        weight:                Relative weight within the rubric (sums to total_weight).
        max_marks:             Maximum marks a student can score on this criterion.
        expected_keywords:     List of keywords/phrases the AI matches against.
        order_index:           Display and evaluation order (0-based).
        created_at:            UTC creation timestamp.
        updated_at:            UTC last-modified timestamp.
    """

    id: uuid.UUID
    rubric_id: uuid.UUID
    criterion_name: str
    weight: float
    max_marks: float
    order_index: int
    created_at: datetime
    updated_at: datetime
    criterion_description: str | None = None
    expected_keywords: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        rubric_id: uuid.UUID,
        criterion_name: str,
        weight: float,
        max_marks: float,
        order_index: int = 0,
        criterion_description: str | None = None,
        expected_keywords: list[str] | None = None,
    ) -> "RubricCriterion":
        """
        Factory method: Create a new RubricCriterion.

        Raises:
            ValueError: If weight or max_marks violate domain invariants.
        """
        from app.core.constants import MAX_KEYWORDS_PER_CRITERION

        keywords = expected_keywords or []

        if not (0.0 < weight <= 1.0):
            raise ValueError(f"weight must be in (0.0, 1.0], got {weight}.")
        if max_marks <= 0:
            raise ValueError(f"max_marks must be > 0, got {max_marks}.")
        if len(keywords) > MAX_KEYWORDS_PER_CRITERION:
            raise ValueError(
                f"expected_keywords length {len(keywords)} exceeds "
                f"maximum {MAX_KEYWORDS_PER_CRITERION}."
            )

        now = datetime.now(timezone.utc)
        return cls(
            id=uuid.uuid4(),
            rubric_id=rubric_id,
            criterion_name=criterion_name.strip(),
            criterion_description=criterion_description,
            weight=weight,
            max_marks=max_marks,
            expected_keywords=keywords,
            order_index=order_index,
            created_at=now,
            updated_at=now,
        )

    @property
    def has_keywords(self) -> bool:
        return bool(self.expected_keywords)

    @property
    def keyword_count(self) -> int:
        return len(self.expected_keywords)

    def effective_marks(self, rubric_total_weight: float, question_max_marks: int) -> float:
        """
        Compute this criterion's share of the question's total marks.

        effective_marks = (criterion.weight / rubric.total_weight) × question.max_marks
        """
        if rubric_total_weight <= 0:
            raise ValueError("rubric_total_weight must be > 0.")
        return (self.weight / rubric_total_weight) * question_max_marks

    def __repr__(self) -> str:
        return (
            f"RubricCriterion(id={self.id}, name='{self.criterion_name}', "
            f"weight={self.weight}, max_marks={self.max_marks})"
        )
