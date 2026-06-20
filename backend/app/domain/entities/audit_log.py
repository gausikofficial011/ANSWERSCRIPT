"""
domain/entities/audit_log.py — AuditLog Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid
from app.core.constants import AuditAction, AuditStatus


@dataclass
class AuditLog:
    action: AuditAction
    resource_type: str
    status: AuditStatus
    user_id: uuid.UUID | None = None
    resource_id: uuid.UUID | None = None
    old_values: dict | None = None
    new_values: dict | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    error_message: str | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
