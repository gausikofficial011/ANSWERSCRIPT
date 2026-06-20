"""
infrastructure/persistence/models/plagiarism_report_model.py — PlagiarismReport ORM Model

Represents a plagiarism/similarity analysis between two student answer sheets in the same exam.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import Float, String, Text, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.persistence.database import Base
from app.core.constants import PlagiarismStatus

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.user_model import UserModel


class PlagiarismReportModel(Base):
    __tablename__ = "plagiarism_reports"
    __table_args__ = (
        UniqueConstraint(
            "source_answer_sheet_id",
            "target_answer_sheet_id",
            name="uq_plagiarism_reports_pair"
        ),
    )

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
    source_answer_sheet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("answer_sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    target_answer_sheet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("answer_sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    similarity_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    highest_similarity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )
    risk_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="CLEAN",
        index=True
    )
    teacher_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    similarity_details: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )
    flagged_questions: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )
    status: Mapped[PlagiarismStatus] = mapped_column(
        String(50),
        default=PlagiarismStatus.DETECTED,
        nullable=False,
        index=True
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
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
    exam: Mapped[ExamModel] = relationship()
    source_sheet: Mapped[AnswerSheetModel] = relationship(
        foreign_keys=[source_answer_sheet_id]
    )
    target_sheet: Mapped[AnswerSheetModel] = relationship(
        foreign_keys=[target_answer_sheet_id]
    )
    reviewer: Mapped[UserModel | None] = relationship()

    def __repr__(self) -> str:
        return f"<PlagiarismReportModel(exam_id={self.exam_id}, similarity={self.similarity_percentage}%, status={self.status})>"
