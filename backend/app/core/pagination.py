"""
core/pagination.py — Pagination Request/Response Contracts

Provides a reusable pagination model used across all list endpoints.
Decoupled from any specific framework — FastAPI Query params are applied
in api/v1/dependencies/pagination.py.
"""

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


@dataclass(frozen=True)
class PaginationParams:
    """
    Immutable pagination parameters extracted from incoming requests.

    Attributes:
        page:  1-based page number.
        limit: Number of items per page (capped at MAX_PAGE_SIZE).
    """
    page: int = 1
    limit: int = DEFAULT_PAGE_SIZE

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if not (1 <= self.limit <= MAX_PAGE_SIZE):
            raise ValueError(f"limit must be between 1 and {MAX_PAGE_SIZE}")

    @property
    def offset(self) -> int:
        """Calculate SQL OFFSET from 1-based page and limit."""
        return (self.page - 1) * self.limit


@dataclass
class PaginatedResponse(Generic[T]):
    """
    Generic paginated response envelope.

    Attributes:
        items:       The list of items for this page.
        total:       Total number of items across all pages.
        page:        Current 1-based page number.
        limit:       Items per page.
        total_pages: Total number of pages.
        has_next:    Whether a next page exists.
        has_prev:    Whether a previous page exists.
    """
    items: list[T] = field(default_factory=list)
    total: int = 0
    page: int = 1
    limit: int = DEFAULT_PAGE_SIZE

    @property
    def total_pages(self) -> int:
        if self.limit == 0:
            return 0
        return max(1, -(-self.total // self.limit))  # ceiling division

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1
