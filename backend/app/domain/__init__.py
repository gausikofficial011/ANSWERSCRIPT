"""
domain/ — Domain Layer (Pure Python, No Framework Dependencies)

This is the innermost layer of Clean Architecture. It has ZERO dependencies
on FastAPI, SQLAlchemy, or any infrastructure library.

Bounded sub-packages:
  entities/       — Rich domain objects with identity and behavior
  value_objects/  — Immutable types with equality by value
  aggregates/     — Consistency boundaries spanning multiple entities
  services/       — Domain logic spanning multiple entities/aggregates
  repositories/   — Abstract interfaces (ports) for data access
  events/         — Domain event definitions (what happened in the domain)
  exceptions/     — Business rule violation exceptions

Dependency rule: NOTHING in this package imports from:
  - app.api
  - app.application
  - app.infrastructure
  - app.ai
  - app.ocr
  - app.storage
  - app.tasks
"""
