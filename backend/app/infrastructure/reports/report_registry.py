"""
infrastructure/reports/report_registry.py — In-memory Export Lifecycle Registry
"""

from __future__ import annotations
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class RegisteredReport:
    report_id: uuid.UUID
    report_type: str
    generated_at: datetime
    requesting_user_id: uuid.UUID
    file_size_bytes: int
    metadata: dict


class ReportRegistry:
    """
    In-memory registry to track report generation events.
    Does not use database tables or migrations.
    """

    def __init__(self) -> None:
        self._reports: dict[uuid.UUID, RegisteredReport] = {}

    def register(
        self,
        report_type: str,
        requesting_user_id: uuid.UUID,
        file_size_bytes: int,
        metadata: dict
    ) -> RegisteredReport:
        """
        Record a report generation event.
        """
        report_id = uuid.uuid4()
        report = RegisteredReport(
            report_id=report_id,
            report_type=report_type,
            generated_at=datetime.utcnow(),
            requesting_user_id=requesting_user_id,
            file_size_bytes=file_size_bytes,
            metadata=metadata
        )
        self._reports[report_id] = report
        return report

    def get_all(self) -> list[RegisteredReport]:
        """
        Retrieve all registered report events.
        """
        return list(self._reports.values())

    def get_by_id(self, report_id: uuid.UUID) -> RegisteredReport | None:
        """
        Retrieve a registered report by its ID.
        """
        return self._reports.get(report_id)

    def clear(self) -> None:
        """
        Clear all entries from the registry.
        """
        self._reports.clear()

    def remove_expired(self, retention_hours: int) -> int:
        """
        Remove expired reports from the registry.
        Returns:
            The number of deleted entries.
        """
        now = datetime.utcnow()
        expired_ids = [
            rep_id for rep_id, rep in self._reports.items()
            if now - rep.generated_at > timedelta(hours=retention_hours)
        ]
        for rep_id in expired_ids:
            del self._reports[rep_id]
        return len(expired_ids)


# Singleton-like global instance
report_registry = ReportRegistry()
