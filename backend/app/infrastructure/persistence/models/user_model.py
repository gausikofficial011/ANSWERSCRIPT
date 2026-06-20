"""
infrastructure/persistence/models/user_model.py — User ORM Model

Represents registered users (admins, teachers) in the system.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.role_model import RoleModel
    from app.infrastructure.persistence.models.teacher_model import TeacherModel
    from app.infrastructure.persistence.models.refresh_token_model import RefreshTokenModel
    from app.infrastructure.persistence.models.notification_model import NotificationModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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
    role: Mapped[RoleModel] = relationship(
        back_populates="users"
    )
    teacher: Mapped[TeacherModel | None] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[List[RefreshTokenModel]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notifications: Mapped[List[NotificationModel]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<UserModel(username={self.username}, email={self.email})>"
