"""domain/events/evaluation_events.py — Evaluation Domain Events"""

from dataclasses import dataclass
from app.domain.events.base_event import BaseDomainEvent


@dataclass(frozen=True)
class EvaluationStarted(BaseDomainEvent):
    """Raised when AI evaluation Celery task begins for an answer sheet."""
    answer_sheet_id: str = ""
    triggered_by: str = ""


@dataclass(frozen=True)
class EvaluationCompleted(BaseDomainEvent):
    """
    Raised when AI evaluation finishes for all questions in an answer sheet.

    Consumers:
      - Application: notify teacher ("Evaluation complete, ready for verification")
      - Application: create audit log
    """
    answer_sheet_id: str = ""
    total_questions_evaluated: int = 0
    ai_total_score: float = 0.0
    max_possible_marks: int = 0


@dataclass(frozen=True)
class ScoreOverridden(BaseDomainEvent):
    """
    Raised when a teacher manually overrides an AI-assigned score.

    Consumers:
      - Application: create audit log (with old + new values)
    """
    evaluation_id: str = ""
    question_id: str = ""
    answer_sheet_id: str = ""
    old_score: float = 0.0
    new_score: float = 0.0
    overridden_by: str = ""   # teacher user_id


@dataclass(frozen=True)
class VerificationSubmitted(BaseDomainEvent):
    """
    Raised when a teacher submits their final verification of an answer sheet.

    Consumers:
      - Application: trigger result generation
      - Application: create audit log
      - Application: notify relevant parties
    """
    answer_sheet_id: str = ""
    verified_by: str = ""   # teacher user_id
    approved: bool = True
    notes: str = ""
