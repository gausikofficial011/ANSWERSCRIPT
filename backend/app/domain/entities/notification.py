"""
domain/entities/notification.py — Notification Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid
from app.core.constants import NotificationType


@dataclass
class Notification:
    user_id: uuid.UUID
    title: str
    message: str
    type: NotificationType
    category: str
    resource_type: str | None = None
    resource_id: uuid.UUID | None = None
    is_read: bool = False
    read_at: datetime | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
