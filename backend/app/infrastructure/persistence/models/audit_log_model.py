"""
infrastructure/persistence/models/audit_log_model.py — AuditLog ORM Model

Represents a system-wide log for security auditing, tracking user and system events.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.persistence.database import Base
from app.core.constants import AuditAction, AuditStatus

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.user_model import UserModel


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    action: Mapped[AuditAction] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        nullable=True
    )
    old_values: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )
    new_values: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    status: Mapped[AuditStatus] = mapped_column(
        String(50),
        nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    user: Mapped[UserModel | None] = relationship()

    def __repr__(self) -> str:
        return f"<AuditLogModel(action={self.action}, user_id={self.user_id}, status={self.status})>"
