"""domain/events/plagiarism_events.py — Plagiarism Detection Domain Events"""

from dataclasses import dataclass
from app.domain.events.base_event import BaseDomainEvent


@dataclass(frozen=True)
class PlagiarismCheckStarted(BaseDomainEvent):
    """Raised when the plagiarism check Celery task begins for an exam."""
    exam_id: str = ""
    triggered_by: str = ""


@dataclass(frozen=True)
class PlagiarismDetected(BaseDomainEvent):
    """
    Raised for each pair of answer sheets flagged above the similarity threshold.

    Consumers:
      - Application: persist plagiarism_report record
      - Application: notify teacher
    """
    exam_id: str = ""
    source_answer_sheet_id: str = ""
    target_answer_sheet_id: str = ""
    similarity_percentage: float = 0.0
    flagged_question_ids: list = None

    def __post_init__(self) -> None:
        # dataclass frozen workaround for mutable default
        if self.flagged_question_ids is None:
            object.__setattr__(self, "flagged_question_ids", [])


@dataclass(frozen=True)
class PlagiarismReviewed(BaseDomainEvent):
    """
    Raised when a teacher reviews and updates the status of a plagiarism report.
    """
    plagiarism_report_id: str = ""
    exam_id: str = ""
    new_status: str = ""   # "confirmed" | "dismissed"
    reviewed_by: str = ""
