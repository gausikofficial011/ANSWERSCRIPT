"""
storage/ — File Storage Subsystem

Self-contained subsystem managing all file persistence operations.

Internal structure:
  uploads/    — Upload reception, validation, and backend-agnostic storage
  reports/    — PDF report generation and storage
  temp/       — Temporary working directory management
  lifecycle/  — File retention policies and scheduled cleanup

Storage Backend Abstraction:
  Current:  LocalFileStorage (filesystem)
  Future:   S3Storage, GCSStorage, AzureBlobStorage
  Swap:     Change only the DI binding in app/dependencies.py

Dependency rules:
  ✅ May import from: app.core, app.domain.exceptions (FileException subclasses)
  ❌ Must NOT import from: app.api, app.application, app.infrastructure.persistence
  ❌ Must NOT import from: app.ai, app.ocr, app.tasks
"""
