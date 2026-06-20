"""
infrastructure/persistence/models/answer_sheet_model.py — AnswerSheet ORM Model

Represents a student's uploaded answer sheet.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, Text, BigInteger, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.infrastructure.persistence.database import Base
from app.core.constants import AnswerSheetStatus

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.exam_model import ExamModel
    from app.infrastructure.persistence.models.student_model import StudentModel
    from app.infrastructure.persistence.models.user_model import UserModel
    from app.infrastructure.persistence.models.ocr_result_model import OCRResultModel
    from app.infrastructure.persistence.models.extracted_answer_model import ExtractedAnswerModel
    from app.infrastructure.persistence.models.question_mapping_model import QuestionMappingModel
    from app.infrastructure.persistence.models.evaluation_model import EvaluationModel
    from app.infrastructure.persistence.models.final_result_model import FinalResultModel


class AnswerSheetModel(Base):
    __tablename__ = "answer_sheets"

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
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )
    original_filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    stored_filename: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False
    )
    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )
    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    page_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    status: Mapped[AnswerSheetStatus] = mapped_column(
        String(50),
        default=AnswerSheetStatus.UPLOADED,
        nullable=False,
        index=True
    )
    file_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    supersedes_answer_sheet_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("answer_sheets.id", ondelete="SET NULL"),
        nullable=True
    )
    superseded_by_answer_sheet_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("answer_sheets.id", ondelete="SET NULL"),
        nullable=True
    )
    processing_status: Mapped[str] = mapped_column(
        String(50),
        default="UPLOADED",
        nullable=False
    )
    queued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    processing_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    plagiarism_flagged: Mapped[bool] = mapped_column(
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

    # ── Relationships ──────────────────────────────────────────────────────────
    exam: Mapped[ExamModel] = relationship(
        back_populates="answer_sheets"
    )
    student: Mapped[StudentModel] = relationship(
        back_populates="answer_sheets"
    )
    uploader: Mapped[UserModel] = relationship()
    ocr_results: Mapped[List[OCRResultModel]] = relationship(
        back_populates="answer_sheet",
        cascade="all, delete-orphan"
    )
    question_mappings: Mapped[List[QuestionMappingModel]] = relationship(
        back_populates="answer_sheet",
        cascade="all, delete-orphan"
    )
    extracted_answers: Mapped[List[ExtractedAnswerModel]] = relationship(
        back_populates="answer_sheet",
        cascade="all, delete-orphan"
    )
    evaluations: Mapped[List[EvaluationModel]] = relationship(
        back_populates="answer_sheet",
        cascade="all, delete-orphan"
    )
    final_result: Mapped[FinalResultModel | None] = relationship(
        back_populates="answer_sheet",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AnswerSheetModel(original_filename={self.original_filename}, status={self.status})>"
