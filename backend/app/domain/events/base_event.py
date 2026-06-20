"""
domain/events/base_event.py — Base Domain Event

All domain events inherit from BaseDomainEvent which provides
a unique event_id, an occurred_at timestamp, and the aggregate
that produced the event.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class BaseDomainEvent:
    """
    Base class for all domain events.

    Attributes:
        event_id:      Unique identifier for this specific event occurrence.
        occurred_at:   UTC timestamp when the event occurred.
        aggregate_id:  ID of the aggregate root that raised this event.
        aggregate_type: Class name of the aggregate (e.g., "AnswerSheet").
    """

    aggregate_id: str
    aggregate_type: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def event_name(self) -> str:
        """Return canonical event name (class name)."""
        return self.__class__.__name__

    def __repr__(self) -> str:
        return (
            f"{self.event_name}("
            f"aggregate_id='{self.aggregate_id}', "
            f"occurred_at='{self.occurred_at.isoformat()}')"
        )
