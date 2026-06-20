"""
infrastructure/persistence/models/evaluation_model.py — Evaluation ORM Model

Represents the evaluation results (AI scores + teacher overrides) for a student answer.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, Text, Float, Integer, Boolean, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.question_mapping_model import QuestionMappingModel
    from app.infrastructure.persistence.models.question_model import QuestionModel
    from app.infrastructure.persistence.models.model_answer_model import ModelAnswerModel
    from app.infrastructure.persistence.models.rubric_model import RubricModel
    from app.infrastructure.persistence.models.user_model import UserModel
    from app.infrastructure.persistence.models.criterion_evaluation_model import CriterionEvaluationModel
    from app.infrastructure.persistence.models.evaluation_revision_model import EvaluationRevisionModel


class EvaluationModel(Base):
    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    answer_sheet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("answer_sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question_mapping_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("question_mappings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    model_answer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("model_answers.id", ondelete="RESTRICT"),
        nullable=False
    )
    rubric_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("rubrics.id", ondelete="SET NULL"),
        nullable=True
    )
    ai_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    max_marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    similarity_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    keyword_match_score: Mapped[float | None] = mapped_column(
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
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    evaluation_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    evaluation_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    explanation: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
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
        UniqueConstraint("answer_sheet_id", "question_id", name="uq_evaluations_sheet_question"),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    answer_sheet: Mapped[AnswerSheetModel] = relationship(
        back_populates="evaluations"
    )
    question_mapping: Mapped[QuestionMappingModel] = relationship()
    question: Mapped[QuestionModel] = relationship()
    model_answer: Mapped[ModelAnswerModel] = relationship()
    rubric: Mapped[RubricModel | None] = relationship()
    verifier: Mapped[UserModel | None] = relationship()
    criterion_evaluations: Mapped[List[CriterionEvaluationModel]] = relationship(
        back_populates="evaluation",
        cascade="all, delete-orphan"
    )
    revisions: Mapped[List[EvaluationRevisionModel]] = relationship(
        back_populates="evaluation",
        cascade="all, delete-orphan",
        order_by="EvaluationRevisionModel.revision_number"
    )

    def __repr__(self) -> str:
        return f"<EvaluationModel(id={self.id}, final_score={self.final_score}, verified={self.is_verified})>"
