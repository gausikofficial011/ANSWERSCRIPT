"""
domain/entities/criterion_evaluation.py — CriterionEvaluation Entity

Records the AI-generated and teacher-verified score for a single
RubricCriterion within a given Evaluation.

Relationship:
  Evaluation (1) ──── (N) CriterionEvaluation
  RubricCriterion (1) ── (N) CriterionEvaluation

Resolution rule for final_score:
  final_score = teacher_score if teacher_score is not None else ai_score
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class CriterionEvaluation:
    """
    Per-criterion scoring record.

    Attributes:
        id:                     UUID primary key.
        evaluation_id:          Parent Evaluation UUID.
        rubric_criterion_id:    The criterion being scored.
        ai_score:               Score assigned by the AI pipeline (None if not run).
        ai_semantic_score:      Raw semantic similarity component (0.0–1.0).
        ai_keyword_score:       Raw keyword match component (0.0–1.0).
        ai_feedback:            Short AI-generated feedback for this criterion.
        teacher_score:          Teacher override score (None if not overridden).
        teacher_feedback:       Teacher's comment on this criterion.
        final_score:            Resolved score (teacher_score ?? ai_score).
        is_verified:            True when teacher has explicitly reviewed this criterion.
        created_at:             UTC creation timestamp.
        updated_at:             UTC last-modified timestamp.
    """

    id: uuid.UUID
    evaluation_id: uuid.UUID
    rubric_criterion_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    ai_score: float | None = None
    ai_semantic_score: float | None = None
    ai_keyword_score: float | None = None
    ai_feedback: str | None = None
    teacher_score: float | None = None
    teacher_feedback: str | None = None
    is_verified: bool = False

    @classmethod
    def create_for_ai(
        cls,
        evaluation_id: uuid.UUID,
        rubric_criterion_id: uuid.UUID,
        ai_score: float,
        ai_semantic_score: float,
        ai_keyword_score: float,
        ai_feedback: str | None = None,
    ) -> "CriterionEvaluation":
        """Factory: Create criterion evaluation from AI pipeline output."""
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid.uuid4(),
            evaluation_id=evaluation_id,
            rubric_criterion_id=rubric_criterion_id,
            ai_score=ai_score,
            ai_semantic_score=ai_semantic_score,
            ai_keyword_score=ai_keyword_score,
            ai_feedback=ai_feedback,
            is_verified=False,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def create_empty(
        cls,
        evaluation_id: uuid.UUID,
        rubric_criterion_id: uuid.UUID,
    ) -> "CriterionEvaluation":
        """
        Factory: Create blank criterion evaluation for MANUAL grading mode.
        Teacher will populate scores via the verification UI.
        """
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid.uuid4(),
            evaluation_id=evaluation_id,
            rubric_criterion_id=rubric_criterion_id,
            ai_score=None,
            is_verified=False,
            created_at=now,
            updated_at=now,
        )

    # ── Domain Logic ──────────────────────────────────────────────────────────

    @property
    def final_score(self) -> float | None:
        """Resolved score: teacher override takes precedence over AI score."""
        return self.teacher_score if self.teacher_score is not None else self.ai_score

    @property
    def has_teacher_override(self) -> bool:
        return self.teacher_score is not None

    @property
    def is_scored(self) -> bool:
        """True if either AI or teacher has provided a score."""
        return self.final_score is not None

    def apply_teacher_override(
        self, score: float, feedback: str | None = None
    ) -> None:
        """
        Apply a teacher score override.
        Does NOT set is_verified — teacher must explicitly verify.
        """
        self.teacher_score = score
        if feedback:
            self.teacher_feedback = feedback
        self.updated_at = datetime.now(timezone.utc)

    def verify(self) -> None:
        """Mark this criterion as verified by the teacher."""
        self.is_verified = True
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return (
            f"CriterionEvaluation(id={self.id}, "
            f"criterion={self.rubric_criterion_id}, "
            f"ai={self.ai_score}, teacher={self.teacher_score}, "
            f"verified={self.is_verified})"
        )
