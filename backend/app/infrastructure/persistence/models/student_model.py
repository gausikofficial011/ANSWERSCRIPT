"""
infrastructure/persistence/models/student_model.py — Student ORM Model

Represents student records in the system.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
    from app.infrastructure.persistence.models.final_result_model import FinalResultModel


class StudentModel(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    student_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )
    class_section: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
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
    answer_sheets: Mapped[List[AnswerSheetModel]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan"
    )
    final_results: Mapped[List[FinalResultModel]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<StudentModel(student_number={self.student_number}, full_name={self.full_name})>"
