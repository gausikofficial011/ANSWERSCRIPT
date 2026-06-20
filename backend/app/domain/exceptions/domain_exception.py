"""
domain/exceptions/domain_exception.py — Base Domain Exceptions

Base exception class and core generic exceptions for the domain layer.
"""

from __future__ import annotations
from uuid import UUID


class DomainException(Exception):
    """
    Base class for all domain-layer exceptions.

    Provides a structured message and optional context.
    Never contains HTTP status codes — those live in core/exceptions.py.
    """

    def __init__(self, message: str, context: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context: dict = context or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.message}')"


class EntityNotFoundException(DomainException):
    """
    Raised when a requested entity does not exist in the system.

    Args:
        entity_type: Human-readable entity name (e.g., "Exam", "AnswerSheet").
        entity_id:   The identifier that was searched for.
    """

    def __init__(self, entity_type: str, entity_id: str | UUID) -> None:
        super().__init__(
            message=f"{entity_type} with id '{entity_id}' was not found.",
            context={"entity_type": entity_type, "entity_id": str(entity_id)},
        )
        self.entity_type = entity_type
        self.entity_id = entity_id


class DuplicateEntityException(DomainException):
    """
    Raised when attempting to create an entity that already exists
    (uniqueness constraint violation at the domain level).

    Args:
        entity_type: Human-readable entity name.
        field:       The unique field (e.g., "email").
        value:       The duplicate value.
    """

    def __init__(self, entity_type: str, field: str, value: str) -> None:
        super().__init__(
            message=f"{entity_type} with {field} '{value}' already exists.",
            context={"entity_type": entity_type, "field": field, "value": value},
        )
        self.entity_type = entity_type
        self.field = field
        self.value = value


class BusinessRuleViolationException(DomainException):
    """
    Raised when a domain business rule is violated.

    Use this for invariant checks that don't fit a more specific exception.

    Args:
        rule:    Human-readable description of the violated rule.
        context: Optional additional context dictionary.
    """

    def __init__(self, rule: str, context: dict | None = None) -> None:
        super().__init__(
            message=f"Business rule violated: {rule}",
            context=context or {},
        )
        self.rule = rule
