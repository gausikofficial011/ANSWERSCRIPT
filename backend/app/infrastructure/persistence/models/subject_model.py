"""
infrastructure/persistence/models/subject_model.py — Subject ORM Model

Represents subjects/courses in the academic context.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.user_model import UserModel
    from app.infrastructure.persistence.models.exam_model import ExamModel


class SubjectModel(Base):
    __tablename__ = "subjects"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
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
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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
    creator: Mapped[UserModel] = relationship()
    exams: Mapped[List[ExamModel]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SubjectModel(code={self.code}, name={self.name})>"
