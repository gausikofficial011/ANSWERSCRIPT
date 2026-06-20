"""
domain/entities/rubric.py — Rubric Aggregate Root

A Rubric defines the structured marking scheme for a Question.
It is the aggregate root: all RubricCriteria are created, modified,
and deleted through the Rubric aggregate.

Design:
  - One active Rubric per Question at any time
  - Locked (immutable) once any CriterionEvaluation references it
  - Versioned: each modification-after-lock creates a new version
  - Grading mode determines whether AI, teacher, or both score criteria
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.core.constants import GradingMode

if TYPE_CHECKING:
    from app.domain.entities.rubric_criterion import RubricCriterion


@dataclass
class Rubric:
    """
    Rubric aggregate root.

    Lifecycle states:
      draft     → active (on first save with criteria)
      active    → locked (when first evaluation uses it)
      locked    → superseded (when new version created)

    Attributes:
        id:            UUID primary key.
        question_id:   The question this rubric belongs to.
        title:         Short label for the rubric.
        description:   Optional detailed description.
        total_weight:  Sum of all criterion weights (enforced invariant).
        version:       Monotonically increasing version number.
        is_active:     True if this is the current rubric for the question.
        grading_mode:  AI, MANUAL, or HYBRID evaluation mode.
        is_locked:     True once any evaluation references this rubric.
                       Populated at load time from DB lookup.
        created_by:    UUID of the teacher who created this rubric.
        created_at:    UTC creation timestamp.
        updated_at:    UTC last-modified timestamp.
        criteria:      Ordered list of RubricCriterion (loaded when needed).
    """

    id: uuid.UUID
    question_id: uuid.UUID
    title: str
    total_weight: float
    version: int
    is_active: bool
    grading_mode: GradingMode
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    is_locked: bool = False
    deleted_at: datetime | None = None
    criteria: list["RubricCriterion"] = field(default_factory=list)


    @classmethod
    def create(
        cls,
        question_id: uuid.UUID,
        title: str,
        created_by: uuid.UUID,
        grading_mode: GradingMode = GradingMode.AI,
        description: str | None = None,
        version: int = 1,
    ) -> "Rubric":
        """
        Factory method: Create a new Rubric aggregate.
        Always starts as version 1, active, unlocked.
        """
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid.uuid4(),
            question_id=question_id,
            title=title,
            description=description,
            total_weight=0.0,   # Computed after criteria are added
            version=version,
            is_active=True,
            grading_mode=grading_mode,
            is_locked=False,
            created_by=created_by,
            created_at=now,
            updated_at=now,
        )

    # ── Domain Invariant Guards ───────────────────────────────────────────────

    def assert_not_locked(self) -> None:
        """
        Raise BusinessRuleViolationException if rubric is locked.
        Call before any mutation operation.
        """
        if self.is_locked:
            from app.domain.exceptions.domain_exception import BusinessRuleViolationException
            raise BusinessRuleViolationException(
                rule=(
                    f"Rubric '{self.id}' (version {self.version}) is locked "
                    "because evaluations exist that reference it. "
                    "Create a new version to make changes."
                )
            )

    def assert_weights_valid(self) -> None:
        """
        Raise BusinessRuleViolationException if criteria weights do not
        sum to total_weight.
        """
        if not self.criteria:
            return
        actual_sum = round(sum(c.weight for c in self.criteria), 10)
        expected = round(self.total_weight, 10)
        if abs(actual_sum - expected) > 1e-9:
            from app.domain.exceptions.domain_exception import BusinessRuleViolationException
            raise BusinessRuleViolationException(
                rule=(
                    f"Criterion weights ({actual_sum}) do not sum to "
                    f"rubric total_weight ({expected})."
                )
            )

    # ── Computed Properties ───────────────────────────────────────────────────

    @property
    def criterion_count(self) -> int:
        return len(self.criteria)

    @property
    def total_max_marks(self) -> float:
        """Sum of max_marks across all criteria."""
        return sum(c.max_marks for c in self.criteria)

    @property
    def is_ai_mode(self) -> bool:
        return self.grading_mode in (GradingMode.AI, GradingMode.HYBRID)

    @property
    def requires_teacher_scoring(self) -> bool:
        return self.grading_mode in (GradingMode.MANUAL, GradingMode.HYBRID)

    def __repr__(self) -> str:
        return (
            f"Rubric(id={self.id}, question_id={self.question_id}, "
            f"version={self.version}, mode={self.grading_mode}, "
            f"locked={self.is_locked})"
        )
