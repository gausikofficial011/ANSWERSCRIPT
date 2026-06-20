"""
infrastructure/persistence/models/criterion_evaluation_model.py — CriterionEvaluation ORM Model

Represents scoring detail for a single RubricCriterion within a student answer evaluation.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import Float, Text, Boolean, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.evaluation_model import EvaluationModel
    from app.infrastructure.persistence.models.rubric_criterion_model import RubricCriterionModel


class CriterionEvaluationModel(Base):
    __tablename__ = "criterion_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    rubric_criterion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rubric_criteria.id", ondelete="CASCADE"),
        nullable=False
    )
    ai_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    ai_semantic_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    ai_keyword_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    ai_feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    teacher_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    teacher_feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    final_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # ── Constraints ───────────────────────────────────────────────────────────
    __table_args__ = (
        UniqueConstraint("evaluation_id", "rubric_criterion_id", name="uq_criterion_evaluations_eval_criterion"),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    evaluation: Mapped[EvaluationModel] = relationship(
        back_populates="criterion_evaluations"
    )
    criterion: Mapped[RubricCriterionModel] = relationship()

    def __repr__(self) -> str:
        return f"<CriterionEvaluationModel(eval_id={self.evaluation_id}, criterion_id={self.rubric_criterion_id}, final_score={self.final_score})>"
