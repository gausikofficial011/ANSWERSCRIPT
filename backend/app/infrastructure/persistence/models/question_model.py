"""
infrastructure/persistence/models/question_model.py — Question ORM Model

Represents a single question within an exam.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.infrastructure.persistence.database import Base
from app.core.constants import QuestionType

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.user_model import UserModel
    from app.infrastructure.persistence.models.model_answer_model import ModelAnswerModel
    from app.infrastructure.persistence.models.rubric_model import RubricModel


class QuestionModel(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    question_type: Mapped[QuestionType] = mapped_column(
        String(50),
        nullable=False
    )
    language: Mapped[str] = mapped_column(
        String(50),
        default="en",
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
        UniqueConstraint("exam_id", "question_number", name="uq_questions_exam_question"),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    exam: Mapped[ExamModel] = relationship(
        back_populates="questions"
    )
    creator: Mapped[UserModel] = relationship()
    model_answer: Mapped[ModelAnswerModel | None] = relationship(
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan"
    )
    rubrics: Mapped[List[RubricModel]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<QuestionModel(exam_id={self.exam_id}, number={self.question_number})>"
