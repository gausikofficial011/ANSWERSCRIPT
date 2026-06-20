"""
domain/repositories/__init__.py — Repository Interface Exports

All abstract repository interfaces (ports) defined in the domain layer.
Infrastructure layer provides concrete implementations (adapters).

Dependency Rule:
  domain/repositories/ ─► (no imports from infrastructure/application/api)
  infrastructure/persistence/repositories/ ─► implements these interfaces
  application/use_cases/ ─► depends ONLY on these abstract interfaces
"""

from app.domain.repositories.base_repository import BaseRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.student_repository import StudentRepository
from app.domain.repositories.subject_repository import SubjectRepository
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.repositories.model_answer_repository import ModelAnswerRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.ocr_result_repository import OCRResultRepository
from app.domain.repositories.extracted_answer_repository import ExtractedAnswerRepository
from app.domain.repositories.question_mapping_repository import QuestionMappingRepository
from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.domain.repositories.final_result_repository import FinalResultRepository
from app.domain.repositories.plagiarism_repository import PlagiarismRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.repositories.notification_repository import NotificationRepository
from app.domain.repositories.role_repository import RoleRepository
from app.domain.repositories.rubric_repository import RubricRepository
from app.domain.repositories.rubric_criterion_repository import RubricCriterionRepository
from app.domain.repositories.criterion_evaluation_repository import CriterionEvaluationRepository
from app.domain.repositories.evaluation_revision_repository import EvaluationRevisionRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "StudentRepository",
    "SubjectRepository",
    "ExamRepository",
    "QuestionRepository",
    "ModelAnswerRepository",
    "AnswerSheetRepository",
    "OCRResultRepository",
    "ExtractedAnswerRepository",
    "QuestionMappingRepository",
    "EvaluationRepository",
    "FinalResultRepository",
    "PlagiarismRepository",
    "AuditLogRepository",
    "NotificationRepository",
    "RoleRepository",
    "RubricRepository",
    "RubricCriterionRepository",
    "CriterionEvaluationRepository",
    "EvaluationRevisionRepository",
]
