"""
infrastructure/persistence/models/plagiarism_similarity_model.py — PlagiarismSimilarity ORM Model
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import Float, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.question_mapping_model import QuestionMappingModel


class PlagiarismSimilarityModel(Base):
    __tablename__ = "plagiarism_similarities"
    __table_args__ = (
        UniqueConstraint(
            "source_question_mapping_id",
            "target_question_mapping_id",
            name="uq_plagiarism_similarities_pair"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
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
    source_question_mapping_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("question_mappings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    target_question_mapping_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("question_mappings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    semantic_similarity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    lexical_similarity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    overlap_similarity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    final_similarity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True
    )
    risk_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    source_sheet: Mapped[AnswerSheetModel] = relationship(
        foreign_keys=[source_answer_sheet_id]
    )
    target_sheet: Mapped[AnswerSheetModel] = relationship(
        foreign_keys=[target_answer_sheet_id]
    )
    source_mapping: Mapped[QuestionMappingModel] = relationship(
        foreign_keys=[source_question_mapping_id]
    )
    target_mapping: Mapped[QuestionMappingModel] = relationship(
        foreign_keys=[target_question_mapping_id]
    )

    def __repr__(self) -> str:
        return f"<PlagiarismSimilarityModel(id={self.id}, final_similarity={self.final_similarity}, risk_level={self.risk_level})>"
