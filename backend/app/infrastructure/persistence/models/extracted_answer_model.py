"""
infrastructure/persistence/models/extracted_answer_model.py — ExtractedAnswer ORM Model

Represents a single student answer segment extracted from the OCR result and mapped to a question.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import Text, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.ocr_result_model import OCRResultModel
    from app.infrastructure.persistence.models.question_model import QuestionModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.evaluation_model import EvaluationModel


class ExtractedAnswerModel(Base):
    __tablename__ = "extracted_answers"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    ocr_result_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ocr_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    answer_sheet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("answer_sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    detected_question_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    extracted_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    extraction_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    bounding_box: Mapped[dict | None] = mapped_column(
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

    # ── Relationships ──────────────────────────────────────────────────────────
    ocr_result: Mapped[OCRResultModel] = relationship(
        back_populates="extracted_answers"
    )
    question: Mapped[QuestionModel] = relationship()
    answer_sheet: Mapped[AnswerSheetModel] = relationship(
        back_populates="extracted_answers"
    )

    def __repr__(self) -> str:
        return f"<ExtractedAnswerModel(question_id={self.question_id}, detected_number={self.detected_question_number})>"
