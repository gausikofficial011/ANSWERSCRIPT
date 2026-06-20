"""domain/events/result_events.py — Result Domain Events"""

from dataclasses import dataclass
from app.domain.events.base_event import BaseDomainEvent


@dataclass(frozen=True)
class ResultGenerated(BaseDomainEvent):
    """
    Raised when a final result record is created for a student.

    Consumers:
      - Application: notify teacher result is ready for review/publication
    """
    answer_sheet_id: str = ""
    student_id: str = ""
    exam_id: str = ""
    total_marks_obtained: float = 0.0
    total_marks_possible: int = 0
    percentage: float = 0.0
    grade: str = ""
    pass_fail_status: str = ""


@dataclass(frozen=True)
class ResultPublished(BaseDomainEvent):
    """
    Raised when a teacher publishes a final result, making it
    visible to students and generating the PDF report.

    Consumers:
      - Application: trigger PDF report generation task
      - Application: create audit log
      - Application: send notification
    """
    result_id: str = ""
    student_id: str = ""
    exam_id: str = ""
    published_by: str = ""   # teacher user_id
