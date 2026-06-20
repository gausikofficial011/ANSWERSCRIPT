"""
api/v1/schemas/pagination_schemas.py — Generic Pagination Schema
"""

from __future__ import annotations

from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedSchemaResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True
