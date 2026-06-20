"""
infrastructure/persistence/models/final_result_model.py — FinalResult ORM Model

Represents the aggregated final marks, percentages, grades, and pass/fail statuses for student exam submissions.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import Float, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.persistence.database import Base
from app.core.constants import PassFailStatus

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.student_model import StudentModel
    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.user_model import UserModel


class FinalResultModel(Base):
    __tablename__ = "final_results"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    answer_sheet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("answer_sheets.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    total_marks_obtained: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    total_marks_possible: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    grade: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )
    pass_fail_status: Mapped[PassFailStatus] = mapped_column(
        String(50),
        nullable=False
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    published_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
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
    answer_sheet: Mapped[AnswerSheetModel] = relationship(
        back_populates="final_result"
    )
    student: Mapped[StudentModel] = relationship(
        back_populates="final_results"
    )
    exam: Mapped[ExamModel] = relationship()
    publisher: Mapped[UserModel | None] = relationship()

    def __repr__(self) -> str:
        return f"<FinalResultModel(student_id={self.student_id}, total={self.total_marks_obtained}/{self.total_marks_possible}, grade={self.grade})>"
