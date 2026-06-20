"""
api/v1/dependencies/pagination.py — Pagination FastAPI Dependencies

Parses page and limit query parameters from incoming requests
and returns a validated PaginationParams domain object.

Usage in routers:
    from app.api.v1.dependencies.pagination import get_pagination

    @router.get("/exams")
    async def list_exams(
        pagination: PaginationParams = Depends(get_pagination),
        db_session: AsyncSession = Depends(get_db),
    ):
        use_case = GetExamsUseCase(exam_repo)
        return await use_case.execute(pagination)
"""

from __future__ import annotations

from fastapi import Query

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.core.pagination import PaginationParams


async def get_pagination(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    limit: int = Query(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"Items per page (max {MAX_PAGE_SIZE}).",
    ),
) -> PaginationParams:
    """
    FastAPI dependency that parses and validates pagination query parameters.

    Returns:
        Validated PaginationParams domain object.
    """
    return PaginationParams(page=page, limit=limit)
