"""
domain/entities/subject.py — Subject Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Subject:
    name: str
    code: str
    created_by: uuid.UUID
    description: str | None = None
    language: str = "en"
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    is_active: bool = True
    deleted_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
