"""
infrastructure/persistence/models/teacher_model.py — Teacher ORM Model

Extends the User model to represent teacher-specific information.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.user_model import UserModel


class TeacherModel(Base):
    __tablename__ = "teachers"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    department: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    employee_code: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True
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
    user: Mapped[UserModel] = relationship(
        back_populates="teacher"
    )

    def __repr__(self) -> str:
        return f"<TeacherModel(employee_code={self.employee_code})>"
