"""
ocr/ — OCR Processing Subsystem

Self-contained subsystem for all image processing and text extraction.

Internal structure:
  preprocessors/   — Image preparation before OCR (OpenCV pipeline)
  extractors/      — Text extraction engine (EasyOCR adapter + TextBlock model)
  segmenters/      — Question and answer boundary detection from extracted text
  question_mapper/ — Maps OCR-detected question numbers to DB Question entities

Dependency rules for this package:
  ✅ May import from: app.core, app.domain (entities, value_objects, exceptions)
  ❌ Must NOT import from: app.api, app.application, app.infrastructure.persistence
  ❌ Must NOT import from: app.ai, app.storage, app.tasks

The application layer accesses this subsystem through:
  app.application.interfaces.ocr_engine_interface
"""
