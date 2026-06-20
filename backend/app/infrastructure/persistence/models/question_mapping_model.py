"""
infrastructure/persistence/models/question_mapping_model.py — QuestionMapping ORM Model
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import Text, Integer, Float, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.question_model import QuestionModel
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.user_model import UserModel


class QuestionMappingModel(Base):
    __tablename__ = "question_mappings"

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
    question_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    detected_question_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    detected_question_label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    extracted_answer_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    start_page: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    end_page: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    mapping_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    duplicate_question_flag: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )
    duplicate_group_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True
    )
    source_ocr_result_ids: Mapped[list[uuid.UUID]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    source_bounding_boxes: Mapped[list[dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    source_page_numbers: Mapped[list[int]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    answer_word_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    answer_character_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    answer_page_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    
    # Teacher Correction support
    corrected_question_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("questions.id", ondelete="SET NULL"),
        nullable=True
    )
    corrected_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True
    )
    corrected_at: Mapped[datetime | None] = mapped_column(
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
    answer_sheet: Mapped[AnswerSheetModel] = relationship(
        back_populates="question_mappings"
    )
    question: Mapped[QuestionModel | None] = relationship(
        foreign_keys=[question_id]
    )
    corrected_question: Mapped[QuestionModel | None] = relationship(
        foreign_keys=[corrected_question_id]
    )
    corrected_by: Mapped[UserModel | None] = relationship(
        foreign_keys=[corrected_by_user_id]
    )

    def __repr__(self) -> str:
        return f"<QuestionMappingModel(answer_sheet_id={self.answer_sheet_id}, question_id={self.question_id}, status={self.status})>"
