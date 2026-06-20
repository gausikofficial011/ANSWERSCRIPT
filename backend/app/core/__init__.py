"""
core/ — Cross-Cutting Concerns

Houses system-wide constants, pagination helpers, HTTP-level exceptions,
and shared security utilities. These are framework-aware helpers that
belong ABOVE the domain layer but below the API layer.

Contents:
  constants.py       — Application-wide enumerations and string constants
  pagination.py      — Pagination request/response dataclasses
  exceptions.py      — HTTP exception factories (maps domain errors → HTTP)
  security.py        — Request-level security helpers (header extraction, etc.)
  dependencies.py    — Shared FastAPI Depends() utilities (not auth-specific)
"""
