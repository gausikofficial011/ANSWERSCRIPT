"""
domain/exceptions/__init__.py — Domain Exception Hierarchy

All exceptions raised from the Domain layer. These are pure Python
exceptions with NO HTTP knowledge. The core/exceptions.py module
handles mapping them to HTTP responses.

Hierarchy:
  DomainException (base)
    ├── EntityNotFoundException
    ├── DuplicateEntityException
    ├── BusinessRuleViolationException
    ├── AuthenticationException
    │   ├── InvalidCredentialsException
    │   └── AccountInactiveException
    ├── AuthorizationException
    ├── OCRException
    │   ├── OCRProcessingException
    │   └── OCRLowConfidenceException
    ├── EvaluationException
    │   └── ModelAnswerMissingException
    └── FileException
        ├── FileTooLargeException
        └── UnsupportedFileTypeException
"""

from app.domain.exceptions.domain_exception import (
    DomainException,
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException,
)
from app.domain.exceptions.auth_exceptions import (
    AuthenticationException,
    InvalidCredentialsException,
    AccountInactiveException,
    AuthorizationException,
)
from app.domain.exceptions.ocr_exceptions import (
    OCRException,
    OCRProcessingException,
    OCRLowConfidenceException,
    QuestionMappingException,
)
from app.domain.exceptions.evaluation_exceptions import (
    EvaluationException,
    ModelAnswerMissingException,
    InvalidScoreException,
)
from app.domain.exceptions.file_exceptions import (
    FileException,
    FileTooLargeException,
    UnsupportedFileTypeException,
)

__all__ = [
    "DomainException",
    "EntityNotFoundException",
    "DuplicateEntityException",
    "BusinessRuleViolationException",
    "AuthenticationException",
    "InvalidCredentialsException",
    "AccountInactiveException",
    "AuthorizationException",
    "OCRException",
    "OCRProcessingException",
    "OCRLowConfidenceException",
    "QuestionMappingException",
    "EvaluationException",
    "ModelAnswerMissingException",
    "InvalidScoreException",
    "FileException",
    "FileTooLargeException",
    "UnsupportedFileTypeException",
]
