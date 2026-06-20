"""domain/events/answer_sheet_events.py — Answer Sheet Domain Events"""

from dataclasses import dataclass
from app.domain.events.base_event import BaseDomainEvent


@dataclass(frozen=True)
class AnswerSheetUploaded(BaseDomainEvent):
    """
    Raised after an answer sheet file is successfully saved to storage
    and its record is persisted in the database.

    Consumers:
      - Application layer: triggers OCR pipeline (queues Celery task)
      - Application layer: creates audit log entry
    """
    exam_id: str = ""
    student_id: str = ""
    uploaded_by: str = ""
    file_path: str = ""
    file_size_bytes: int = 0


@dataclass(frozen=True)
class AnswerSheetDeleted(BaseDomainEvent):
    """
    Raised when an answer sheet and its associated files are deleted.

    Consumers:
      - Application layer: creates audit log entry
      - Storage lifecycle: schedules file deletion
    """
    deleted_by: str = ""
    exam_id: str = ""
    student_id: str = ""
