"""
domain/entities/student.py — Student Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Student:
    student_number: str
    full_name: str
    email: str | None = None
    class_section: str | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    deleted_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
