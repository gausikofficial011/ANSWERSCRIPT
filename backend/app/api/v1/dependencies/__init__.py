"""
api/v1/dependencies/__init__.py — FastAPI Dependency Injection Functions

This package contains all FastAPI Depends() callables used by routers.
Separating these from routers keeps routers thin and testable.

Sub-modules:
  auth.py       — Current user extraction and role enforcement
  pagination.py — Pagination parameter parsing from query strings
  common.py     — DB session, repository, and service injection
"""
