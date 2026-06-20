"""
infrastructure/persistence/models/rubric_criterion_model.py — RubricCriterion ORM Model

Represents a single scoring criterion belonging to a Rubric.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, Text, Float, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.rubric_model import RubricModel


class RubricCriterionModel(Base):
    __tablename__ = "rubric_criteria"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    rubric_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rubrics.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    criterion_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    criterion_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    max_marks: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    expected_keywords: Mapped[List[str]] = mapped_column(
        JSONB,
        server_default="[]",
        nullable=False
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
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
    rubric: Mapped[RubricModel] = relationship(
        back_populates="criteria"
    )

    def __repr__(self) -> str:
        return f"<RubricCriterionModel(rubric_id={self.rubric_id}, name={self.criterion_name})>"
