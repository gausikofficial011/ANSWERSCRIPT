"""
infrastructure/persistence/models/notification_model.py — Notification ORM Model

Represents in-app notifications generated for teachers and admins.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.persistence.database import Base
from app.core.constants import NotificationType

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.user_model import UserModel


class NotificationModel(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    type: Mapped[NotificationType] = mapped_column(
        String(50),
        nullable=False
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    resource_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        nullable=True
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    read_at: Mapped[datetime | None] = mapped_column(
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
    user: Mapped[UserModel] = relationship(
        back_populates="notifications"
    )

    # Note: Using back_populates requires us to add 'notifications' to UserModel.
    # We did this in user_model.py!

    def __repr__(self) -> str:
        return f"<NotificationModel(user_id={self.user_id}, category={self.category}, is_read={self.is_read})>"
