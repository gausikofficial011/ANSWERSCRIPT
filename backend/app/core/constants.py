"""
core/constants.py — System-Wide Constants and Enumerations

All application-level enumerations and string constants live here.
Domain-specific enumerations belong in domain/entities/*.py instead.

Design note:
  - String values match database ENUM labels exactly to avoid mapping overhead.
  - Python enums are used for type safety throughout the codebase.
"""

from enum import Enum


# ── User Roles ────────────────────────────────────────────────────────────────

class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"


# ── Answer Sheet Processing Status ────────────────────────────────────────────

class AnswerSheetStatus(str, Enum):
    UPLOADED = "UPLOADED"
    QUEUED_FOR_OCR = "QUEUED_FOR_OCR"
    OCR_PROCESSING = "OCR_PROCESSING"
    OCR_COMPLETED = "OCR_COMPLETED"
    QUESTION_DETECTION = "QUESTION_DETECTION"
    ANSWER_SEGMENTATION = "ANSWER_SEGMENTATION"
    QUESTION_MAPPING = "QUESTION_MAPPING"
    MAPPING_COMPLETED = "MAPPING_COMPLETED"
    EVALUATION_PROCESSING = "EVALUATION_PROCESSING"
    EVALUATION_COMPLETED = "EVALUATION_COMPLETED"
    TEACHER_REVIEW_PENDING = "TEACHER_REVIEW_PENDING"
    VERIFIED = "VERIFIED"
    PUBLISHED = "PUBLISHED"
    PLAGIARISM_REVIEW_PENDING = "PLAGIARISM_REVIEW_PENDING"
    FAILED = "FAILED"
    SUPERSEDED = "SUPERSEDED"


# ── OCR Result Statuses ───────────────────────────────────────────────────────

class OCRResultStatus(str, Enum):
    OCR_PENDING = "OCR_PENDING"
    OCR_PROCESSING = "OCR_PROCESSING"
    OCR_COMPLETED = "OCR_COMPLETED"
    OCR_LOW_CONFIDENCE = "OCR_LOW_CONFIDENCE"
    OCR_FAILED = "OCR_FAILED"


# ── Exam Status ───────────────────────────────────────────────────────────────

class ExamStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


# ── Grading Modes ─────────────────────────────────────────────────────────────

class GradingMode(str, Enum):
    AI = "ai"
    MANUAL = "manual"
    HYBRID = "hybrid"


# ── Question Types ────────────────────────────────────────────────────────────

class QuestionType(str, Enum):
    SHORT = "short"
    LONG = "long"
    MCQ = "mcq"
    DESCRIPTIVE = "descriptive"


# ── Plagiarism Report Status ──────────────────────────────────────────────────

class PlagiarismStatus(str, Enum):
    DETECTED = "DETECTED"
    CONFIRMED_PLAGIARISM = "CONFIRMED_PLAGIARISM"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    DISMISSED = "DISMISSED"


# ── Pass/Fail Status ──────────────────────────────────────────────────────────

class PassFailStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    ABSENT = "absent"
    INCOMPLETE = "incomplete"


# ── Notification Types ────────────────────────────────────────────────────────

class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


# ── Notification Categories ───────────────────────────────────────────────────

class NotificationCategory(str, Enum):
    OCR_COMPLETE = "ocr_complete"
    OCR_FAILED = "ocr_failed"
    EVALUATION_COMPLETE = "evaluation_complete"
    RESULT_READY = "result_ready"
    RESULT_PUBLISHED = "result_published"
    PLAGIARISM_DETECTED = "plagiarism_detected"
    VERIFICATION_REQUIRED = "verification_required"
    REPORT_READY = "report_ready"
    SYSTEM = "system"


# ── Audit Log Actions ─────────────────────────────────────────────────────────

class AuditAction(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DEACTIVATED = "user_deactivated"
    PASSWORD_CHANGED = "password_changed"
    
    # Subjects
    SUBJECT_CREATED = "subject_created"
    SUBJECT_UPDATED = "subject_updated"
    SUBJECT_DELETED = "subject_deleted"

    # Students
    STUDENT_CREATED = "student_created"
    STUDENT_UPDATED = "student_updated"
    STUDENT_DELETED = "student_deleted"

    # Exams
    EXAM_CREATED = "exam_created"
    EXAM_UPDATED = "exam_updated"
    EXAM_CLOSED = "exam_closed"
    EXAM_DELETED = "exam_deleted"

    # Questions
    QUESTION_CREATED = "question_created"
    QUESTION_UPDATED = "question_updated"
    QUESTION_DELETED = "question_deleted"

    # Model Answers
    MODEL_ANSWER_CREATED = "model_answer_created"
    MODEL_ANSWER_UPDATED = "model_answer_updated"
    MODEL_ANSWER_DELETED = "model_answer_deleted"

    # Rubrics
    RUBRIC_CREATED = "rubric_created"
    RUBRIC_UPDATED = "rubric_updated"
    RUBRIC_DELETED = "rubric_deleted"

    # Answer Sheets
    ANSWER_SHEET_UPLOADED = "answer_sheet_uploaded"
    ANSWER_SHEET_DELETED = "answer_sheet_deleted"
    ANSWER_SHEET_REPLACED = "answer_sheet_replaced"
    ANSWER_SHEET_STATUS_CHANGED = "answer_sheet_status_changed"
    ANSWER_SHEET_QUEUED = "answer_sheet_queued"

    OCR_TRIGGERED = "ocr_triggered"
    EVALUATION_TRIGGERED = "evaluation_triggered"
    SCORE_OVERRIDDEN = "score_overridden"
    VERIFICATION_SUBMITTED = "verification_submitted"
    RESULT_GENERATED = "result_generated"
    RESULT_PUBLISHED = "result_published"
    PLAGIARISM_CHECK_RUN = "plagiarism_check_run"
    PLAGIARISM_REVIEWED = "plagiarism_reviewed"
    PLAGIARISM_DETECTED = "plagiarism_detected"
    PLAGIARISM_CONFIRMED = "plagiarism_confirmed"
    PLAGIARISM_DISMISSED = "plagiarism_dismissed"
    REPORT_GENERATED = "report_generated"
    AUTHORIZATION_FAILED = "authorization_failed"
    EXPORT_GENERATED = "export_generated"




# ── Audit Status ──────────────────────────────────────────────────────────────

class AuditStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"


# ── Grade Scale ───────────────────────────────────────────────────────────────

class LetterGrade(str, Enum):
    O = "O"       # Outstanding  ≥ 90%
    A_PLUS = "A+" # Excellent    ≥ 80%
    A = "A"       # Very Good    ≥ 70%
    B_PLUS = "B+" # Good         ≥ 60%
    B = "B"       # Above Avg    ≥ 50%
    C = "C"       # Average      ≥ 40%
    F = "F"       # Fail         < 40%


# ── Grade Boundaries ─────────────────────────────────────────────────────────
# Percentage → Letter Grade mapping (inclusive lower bound)

GRADE_BOUNDARIES: list[tuple[float, LetterGrade]] = [
    (90.0, LetterGrade.O),
    (80.0, LetterGrade.A_PLUS),
    (70.0, LetterGrade.A),
    (60.0, LetterGrade.B_PLUS),
    (50.0, LetterGrade.B),
    (40.0, LetterGrade.C),
    (0.0, LetterGrade.F),
]


# ── File Upload Limits ────────────────────────────────────────────────────────

MAX_UPLOAD_SIZE_BYTES: int = 100 * 1024 * 1024   # 100 MB (per user decision)
MAX_PAGE_COUNT: int = 100                          # 100 pages (per user decision)
ALLOWED_MIME_TYPES: frozenset[str] = frozenset({
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/tiff",
})
ALLOWED_EXTENSIONS: frozenset[str] = frozenset({
    ".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"
})


# ── OCR Constants ─────────────────────────────────────────────────────────────

OCR_MIN_CONFIDENCE: float = 0.6          # Blocks below this are flagged
OCR_QUESTION_MAP_HIGH: float = 0.9       # Auto-map threshold
OCR_QUESTION_MAP_MEDIUM: float = 0.7     # Map + flag for review

MAX_KEYWORDS_PER_CRITERION: int = 20


# ── Plagiarism Thresholds ─────────────────────────────────────────────────────


PLAGIARISM_DEFAULT_THRESHOLD: float = 0.85   # Configurable per exam (default)
PLAGIARISM_SUSPICIOUS_THRESHOLD: float = 0.60


# ── AI Scoring Defaults ───────────────────────────────────────────────────────

AI_DEFAULT_SEMANTIC_WEIGHT: float = 0.6  # Configurable per exam (user decision)
AI_DEFAULT_KEYWORD_WEIGHT: float = 0.4


# ── Pagination ────────────────────────────────────────────────────────────────

DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100


# ── Token Expiry ──────────────────────────────────────────────────────────────

ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
REFRESH_TOKEN_EXPIRE_DAYS: int = 7
