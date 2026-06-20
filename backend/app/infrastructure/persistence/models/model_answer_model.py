"""
infrastructure/persistence/models/model_answer_model.py — ModelAnswer ORM Model

Represents the teacher's reference answer for a question.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.question_model import QuestionModel
    from app.infrastructure.persistence.models.user_model import UserModel


class ModelAnswerModel(Base):
    __tablename__ = "model_answers"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    answer_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    keywords: Mapped[List[str] | None] = mapped_column(
        JSONB,
        nullable=True
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

    # ── Relationships ──────────────────────────────────────────────────────────
    question: Mapped[QuestionModel] = relationship(
        back_populates="model_answer"
    )
    creator: Mapped[UserModel] = relationship()

    def __repr__(self) -> str:
        return f"<ModelAnswerModel(question_id={self.question_id})>"
