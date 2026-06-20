"""
domain/entities/user.py — User Domain Entity

Pure Python representation of a User.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class User:
    email: str
    username: str
    hashed_password: str
    full_name: str
    role_id: uuid.UUID | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    is_active: bool = True
    is_verified: bool = False
    last_login_at: datetime | None = None
    deleted_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    role: str | None = None

