"""
infrastructure/persistence/models/ocr_result_model.py — OCRResult ORM Model

Represents the text and layout structures extracted from an answer sheet via OCR.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import Text, String, Float, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.extracted_answer_model import ExtractedAnswerModel


class OCRResultModel(Base):
    __tablename__ = "ocr_results"

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
    page_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    extracted_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    bounding_boxes: Mapped[list[dict]] = mapped_column(
        JSONB,
        nullable=False
    )
    low_confidence_flag: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    average_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    words_detected: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    processing_time: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    ocr_engine_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    preprocessing_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    original_image_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )
    processed_image_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="OCR_PENDING",
        nullable=False
    )
    language_detected: Mapped[str | None] = mapped_column(
        String(50),
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

    __table_args__ = (
        UniqueConstraint("answer_sheet_id", "page_number", name="uq_ocr_results_sheet_page"),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    answer_sheet: Mapped[AnswerSheetModel] = relationship(
        back_populates="ocr_results"
    )
    extracted_answers: Mapped[List[ExtractedAnswerModel]] = relationship(
        back_populates="ocr_result",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<OCRResultModel(answer_sheet_id={self.answer_sheet_id}, page={self.page_number}, status={self.status})>"
