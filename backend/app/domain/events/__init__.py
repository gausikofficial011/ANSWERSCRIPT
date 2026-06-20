"""
domain/events/__init__.py — Domain Events

Domain events represent facts that happened within the domain.
They are named in past tense and are immutable.

Consumers:
  - Application layer: reacts to events to trigger side effects
    (notifications, Celery tasks, audit logging)
  - Infrastructure layer: publishes events to async message queue (future)

Design:
  - Events are pure dataclasses with no behaviour
  - BaseDomainEvent provides timestamp and event_id
  - Events NEVER import from infrastructure or application layers
"""

from app.domain.events.base_event import BaseDomainEvent
from app.domain.events.answer_sheet_events import (
    AnswerSheetUploaded,
    AnswerSheetDeleted,
)
from app.domain.events.ocr_events import (
    OCRProcessingStarted,
    OCRCompleted,
    OCRFailed,
    QuestionMappingCompleted,
    QuestionMappingRequiresReview,
)
from app.domain.events.evaluation_events import (
    EvaluationStarted,
    EvaluationCompleted,
    ScoreOverridden,
    VerificationSubmitted,
)
from app.domain.events.result_events import (
    ResultGenerated,
    ResultPublished,
)
from app.domain.events.plagiarism_events import (
    PlagiarismCheckStarted,
    PlagiarismDetected,
    PlagiarismReviewed,
)

__all__ = [
    "BaseDomainEvent",
    "AnswerSheetUploaded",
    "AnswerSheetDeleted",
    "OCRProcessingStarted",
    "OCRCompleted",
    "OCRFailed",
    "QuestionMappingCompleted",
    "QuestionMappingRequiresReview",
    "EvaluationStarted",
    "EvaluationCompleted",
    "ScoreOverridden",
    "VerificationSubmitted",
    "ResultGenerated",
    "ResultPublished",
    "PlagiarismCheckStarted",
    "PlagiarismDetected",
    "PlagiarismReviewed",
]
