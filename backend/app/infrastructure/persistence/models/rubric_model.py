"""
infrastructure/persistence/models/rubric_model.py — Rubric ORM Model

Represents a versioned rubric for evaluating student answers.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, Text, Float, Integer, Boolean, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.infrastructure.persistence.database import Base
from app.core.constants import GradingMode

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.question_model import QuestionModel
    from app.infrastructure.persistence.models.rubric_criterion_model import RubricCriterionModel
    from app.infrastructure.persistence.models.user_model import UserModel


class RubricModel(Base):
    __tablename__ = "rubrics"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    total_weight: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    grading_mode: Mapped[GradingMode] = mapped_column(
        String(50),
        default=GradingMode.AI,
        nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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
        UniqueConstraint("question_id", "version", name="uq_rubrics_question_version"),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    question: Mapped[QuestionModel] = relationship(
        back_populates="rubrics"
    )
    criteria: Mapped[List[RubricCriterionModel]] = relationship(
        back_populates="rubric",
        cascade="all, delete-orphan",
        order_by="RubricCriterionModel.order_index"
    )
    creator: Mapped[UserModel] = relationship()

    def __repr__(self) -> str:
        return f"<RubricModel(question_id={self.question_id}, version={self.version}, active={self.is_active})>"
