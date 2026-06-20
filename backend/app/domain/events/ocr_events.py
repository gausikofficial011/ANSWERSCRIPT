"""domain/events/ocr_events.py — OCR Processing Domain Events"""

from dataclasses import dataclass
from app.domain.events.base_event import BaseDomainEvent


@dataclass(frozen=True)
class OCRProcessingStarted(BaseDomainEvent):
    """Raised when the OCR Celery task begins processing an answer sheet."""
    answer_sheet_id: str = ""
    triggered_by: str = ""  # user_id or "system"


@dataclass(frozen=True)
class OCRCompleted(BaseDomainEvent):
    """
    Raised when OCR extraction finishes successfully.

    Consumers:
      - Application: trigger evaluation pipeline
      - Application: notify teacher ("OCR complete for sheet X")
      - Application: create audit log
    """
    answer_sheet_id: str = ""
    overall_confidence: float = 0.0
    page_count: int = 0
    language_detected: str = ""
    processing_time_ms: int = 0


@dataclass(frozen=True)
class OCRFailed(BaseDomainEvent):
    """
    Raised when OCR processing fails after all retries.

    Consumers:
      - Application: mark sheet as failed
      - Application: notify teacher
      - Application: create audit log
    """
    answer_sheet_id: str = ""
    error_reason: str = ""
    retry_count: int = 0


@dataclass(frozen=True)
class QuestionMappingCompleted(BaseDomainEvent):
    """
    Raised when all detected questions are successfully mapped to
    the exam's registered questions with high confidence.
    """
    answer_sheet_id: str = ""
    mapped_count: int = 0
    total_questions: int = 0


@dataclass(frozen=True)
class QuestionMappingRequiresReview(BaseDomainEvent):
    """
    Raised when one or more questions could not be confidently mapped.
    Teacher must manually assign via the verification UI.
    """
    answer_sheet_id: str = ""
    unmapped_count: int = 0
    low_confidence_count: int = 0
