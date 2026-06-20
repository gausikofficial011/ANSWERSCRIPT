"""
domain/entities/__init__.py — Domain Entity Exports

Exposes all pure Python domain entities for clean imports across application layers.
"""

from app.domain.entities.role import Role
from app.domain.entities.user import User
from app.domain.entities.student import Student
from app.domain.entities.subject import Subject
from app.domain.entities.exam import Exam
from app.domain.entities.question import Question
from app.domain.entities.model_answer import ModelAnswer
from app.domain.entities.rubric import Rubric
from app.domain.entities.rubric_criterion import RubricCriterion
from app.domain.entities.answer_sheet import AnswerSheet
from app.domain.entities.ocr_result import OCRResult
from app.domain.entities.extracted_answer import ExtractedAnswer
from app.domain.entities.question_mapping import QuestionMapping
from app.domain.entities.evaluation import Evaluation
from app.domain.entities.evaluation_revision import EvaluationRevision
from app.domain.entities.criterion_evaluation import CriterionEvaluation
from app.domain.entities.final_result import FinalResult
from app.domain.entities.plagiarism_report import PlagiarismReport
from app.domain.entities.audit_log import AuditLog
from app.domain.entities.notification import Notification
from app.domain.entities.refresh_token import RefreshToken

__all__ = [
    "Role",
    "User",
    "Student",
    "Subject",
    "Exam",
    "Question",
    "ModelAnswer",
    "Rubric",
    "RubricCriterion",
    "AnswerSheet",
    "OCRResult",
    "ExtractedAnswer",
    "QuestionMapping",
    "Evaluation",
    "EvaluationRevision",
    "CriterionEvaluation",
    "FinalResult",
    "PlagiarismReport",
    "AuditLog",
    "Notification",
    "RefreshToken",
]
