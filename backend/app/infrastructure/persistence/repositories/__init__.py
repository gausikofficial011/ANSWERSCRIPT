"""
infrastructure/persistence/repositories/__init__.py — Repository Exports

Exposes concrete SQLAlchemy repository implementations (adapters) for data persistence.
"""

from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository
from app.infrastructure.persistence.repositories.sql_role_repository import SqlRoleRepository
from app.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository
from app.infrastructure.persistence.repositories.sql_student_repository import SqlStudentRepository
from app.infrastructure.persistence.repositories.sql_subject_repository import SqlSubjectRepository
from app.infrastructure.persistence.repositories.sql_exam_repository import SqlExamRepository
from app.infrastructure.persistence.repositories.sql_question_repository import SqlQuestionRepository
from app.infrastructure.persistence.repositories.sql_model_answer_repository import SqlModelAnswerRepository
from app.infrastructure.persistence.repositories.sql_rubric_repository import SqlRubricRepository
from app.infrastructure.persistence.repositories.sql_rubric_criterion_repository import SqlRubricCriterionRepository
from app.infrastructure.persistence.repositories.sql_answer_sheet_repository import SqlAnswerSheetRepository
from app.infrastructure.persistence.repositories.sql_ocr_result_repository import SqlOCRResultRepository
from app.infrastructure.persistence.repositories.sql_extracted_answer_repository import SqlExtractedAnswerRepository
from app.infrastructure.persistence.repositories.sql_question_mapping_repository import SqlQuestionMappingRepository
from app.infrastructure.persistence.repositories.sql_evaluation_repository import SqlEvaluationRepository
from app.infrastructure.persistence.repositories.sql_evaluation_revision_repository import SqlEvaluationRevisionRepository
from app.infrastructure.persistence.repositories.sql_criterion_evaluation_repository import SqlCriterionEvaluationRepository
from app.infrastructure.persistence.repositories.sql_final_result_repository import SqlFinalResultRepository
from app.infrastructure.persistence.repositories.sql_plagiarism_repository import SqlPlagiarismRepository
from app.infrastructure.persistence.repositories.sql_plagiarism_similarity_repository import SqlPlagiarismSimilarityRepository
from app.infrastructure.persistence.repositories.sql_audit_log_repository import SqlAuditLogRepository
from app.infrastructure.persistence.repositories.sql_notification_repository import SqlNotificationRepository

__all__ = [
    "SqlBaseRepository",
    "SqlRoleRepository",
    "SqlUserRepository",
    "SqlStudentRepository",
    "SqlSubjectRepository",
    "SqlExamRepository",
    "SqlQuestionRepository",
    "SqlModelAnswerRepository",
    "SqlRubricRepository",
    "SqlRubricCriterionRepository",
    "SqlAnswerSheetRepository",
    "SqlOCRResultRepository",
    "SqlExtractedAnswerRepository",
    "SqlQuestionMappingRepository",
    "SqlEvaluationRepository",
    "SqlEvaluationRevisionRepository",
    "SqlCriterionEvaluationRepository",
    "SqlFinalResultRepository",
    "SqlPlagiarismRepository",
    "SqlPlagiarismSimilarityRepository",
    "SqlAuditLogRepository",
    "SqlNotificationRepository",
]
