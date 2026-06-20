"""
infrastructure/persistence/models/exam_model.py — Exam ORM Model

Represents a scheduled exam containing questions and scoring configurations.
"""

from __future__ import annotations

from datetime import date, datetime
import uuid
from sqlalchemy import String, Text, Integer, Date, ForeignKey, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.infrastructure.persistence.database import Base
from app.core.constants import ExamStatus

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.subject_model import SubjectModel
    from app.infrastructure.persistence.models.user_model import UserModel
    from app.infrastructure.persistence.models.question_model import QuestionModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel


class ExamModel(Base):
    __tablename__ = "exams"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"),
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
    exam_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )
    total_marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    passing_marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    status: Mapped[ExamStatus] = mapped_column(
        String(50),
        default=ExamStatus.DRAFT,
        nullable=False
    )
    scoring_config: Mapped[dict | None] = mapped_column(
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
    subject: Mapped[SubjectModel] = relationship(
        back_populates="exams"
    )
    creator: Mapped[UserModel] = relationship()
    questions: Mapped[List[QuestionModel]] = relationship(
        back_populates="exam",
        cascade="all, delete-orphan"
    )
    answer_sheets: Mapped[List[AnswerSheetModel]] = relationship(
        back_populates="exam",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ExamModel(title={self.title}, date={self.exam_date})>"
