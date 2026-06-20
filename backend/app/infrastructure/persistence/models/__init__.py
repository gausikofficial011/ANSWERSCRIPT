"""
infrastructure/persistence/models/__init__.py — Model package exports

All SQLAlchemy ORM models are imported here to ensure they are registered
with Base.metadata before Alembic migrations or database initialization.
"""

from app.infrastructure.persistence.models.role_model import RoleModel
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.models.teacher_model import TeacherModel
from app.infrastructure.persistence.models.student_model import StudentModel
from app.infrastructure.persistence.models.subject_model import SubjectModel
from app.infrastructure.persistence.models.exam_model import ExamModel
from app.infrastructure.persistence.models.question_model import QuestionModel
from app.infrastructure.persistence.models.model_answer_model import ModelAnswerModel
from app.infrastructure.persistence.models.rubric_model import RubricModel
from app.infrastructure.persistence.models.rubric_criterion_model import RubricCriterionModel
from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
from app.infrastructure.persistence.models.ocr_result_model import OCRResultModel
from app.infrastructure.persistence.models.extracted_answer_model import ExtractedAnswerModel
from app.infrastructure.persistence.models.question_mapping_model import QuestionMappingModel
from app.infrastructure.persistence.models.evaluation_model import EvaluationModel
from app.infrastructure.persistence.models.evaluation_revision_model import EvaluationRevisionModel
from app.infrastructure.persistence.models.criterion_evaluation_model import CriterionEvaluationModel
from app.infrastructure.persistence.models.final_result_model import FinalResultModel
from app.infrastructure.persistence.models.plagiarism_report_model import PlagiarismReportModel
from app.infrastructure.persistence.models.plagiarism_similarity_model import PlagiarismSimilarityModel
from app.infrastructure.persistence.models.audit_log_model import AuditLogModel
from app.infrastructure.persistence.models.notification_model import NotificationModel
from app.infrastructure.persistence.models.refresh_token_model import RefreshTokenModel

__all__ = [
    "RoleModel",
    "UserModel",
    "TeacherModel",
    "StudentModel",
    "SubjectModel",
    "ExamModel",
    "QuestionModel",
    "ModelAnswerModel",
    "RubricModel",
    "RubricCriterionModel",
    "AnswerSheetModel",
    "OCRResultModel",
    "ExtractedAnswerModel",
    "QuestionMappingModel",
    "EvaluationModel",
    "EvaluationRevisionModel",
    "CriterionEvaluationModel",
    "FinalResultModel",
    "PlagiarismReportModel",
    "PlagiarismSimilarityModel",
    "AuditLogModel",
    "NotificationModel",
    "RefreshTokenModel",
]
