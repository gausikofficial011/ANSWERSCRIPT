"""
domain/entities/refresh_token.py — RefreshToken Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class RefreshToken:
    user_id: uuid.UUID
    token_hash: str
    expires_at: datetime
    is_revoked: bool = False
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
