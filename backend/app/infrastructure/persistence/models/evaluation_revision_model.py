"""
infrastructure/persistence/models/evaluation_revision_model.py — EvaluationRevision ORM Model

Tracks historical revisions made to an evaluation score by teachers.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import Float, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.evaluation_model import EvaluationModel
    from app.infrastructure.persistence.models.user_model import UserModel


class EvaluationRevisionModel(Base):
    __tablename__ = "evaluation_revisions"

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
    revision_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    previous_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    new_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    previous_feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    new_feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    changed_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
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

    # ── Relationships ──────────────────────────────────────────────────────────
    evaluation: Mapped[EvaluationModel] = relationship(
        back_populates="revisions"
    )
    changer: Mapped[UserModel] = relationship()

    def __repr__(self) -> str:
        return f"<EvaluationRevisionModel(eval_id={self.evaluation_id}, revision={self.revision_number}, new_score={self.new_score})>"
