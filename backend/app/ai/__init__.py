"""
ai/ — AI Evaluation Subsystem

A self-contained subsystem responsible for all AI/NLP operations.
Organized as a bounded sub-module within the infrastructure boundary.

Internal structure (Clean Architecture within a subsystem):
  embeddings/     — Text-to-vector embedding (abstract + implementations)
  evaluation/     — Scoring orchestration using embeddings
  similarity/     — Cosine, keyword, pairwise similarity algorithms
  multilingual/   — Language detection and text normalization
  prompts/        — Prompt templates for future LLM integration

Dependency rules for this package:
  ✅ May import from: app.core, app.domain (entities, value_objects)
  ❌ Must NOT import from: app.api, app.application, app.infrastructure.persistence
  ❌ Must NOT import from: app.ocr, app.storage, app.tasks

Application layer accesses this subsystem through interfaces defined in:
  app.application.interfaces.evaluation_model_interface
"""
