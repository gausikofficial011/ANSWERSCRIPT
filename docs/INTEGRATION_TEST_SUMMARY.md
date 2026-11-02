# Integration Test Summary - AI Answer Evaluation System

Integration tests verify interactions between API endpoints, databases, and Celery background workers.

---

## 1. Test Coverage Details

* **Authentication API**:
  - Validates login requests, JWT token signature validation, and password hashing matches.
* **Syllabus Config Flow**:
  - Tests Subject and Exam CRUD operations, checking database constraints and cascade deletions.
* **Upload API & Database Transaction**:
  - Verifies that answer sheet upload writes to file storage, commits db records, and properly triggers asynchronous OCR tasks without concurrency locks.
* **Results Sync Engine**:
  - Tests that updating individual question evaluations correctly recalculates aggregate student scores.

---

## 2. Test Command
To execute integration tests:
```bash
cd backend
.venv/Scripts/pytest tests/integration/
```
