# IntelliGrade — PostgreSQL Database Schema & Relational Specifications

**Database Engine:** PostgreSQL 15 (Asynchronous via SQLAlchemy 2.0 & asyncpg)  
**Schema Version:** 1.0.0-rc Enterprise  
**Primary Keys:** UUID (v4) for distributed safety and collision avoidance

---

## 1. Domain Entities & Table Directory

The database consists of 28 core domain tables structured across four operational domains:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      DATABASE DOMAIN SCHEMAS                           │
├──────────────────────┬─────────────────────────────────────────────────┤
│ Identity & Tenant    │ users, roles, permissions, user_roles,          │
│                      │ role_permissions, institutions, departments     │
├──────────────────────┼─────────────────────────────────────────────────┤
│ Curriculum & Exam    │ programs, classes, subjects, exams, questions,  │
│                      │ model_answers, rubrics, rubric_criteria         │
├──────────────────────┼─────────────────────────────────────────────────┤
│ Script & Assessment  │ students, answer_sheets, answer_sheet_pages,    │
│                      │ ocr_results, ocr_regions, question_mappings,    │
│                      │ evaluations, criterion_evaluations, revisions   │
├──────────────────────┼─────────────────────────────────────────────────┤
│ Integrity & Governed │ plagiarism_reports, plagiarism_similarities,    │
│ Results              │ final_results, result_publications, audit_logs  │
└──────────────────────┴─────────────────────────────────────────────────┘
```

---

## 2. Core Relational Entities

### `users`
- `id` (UUID, PK)
- `email` (VARCHAR(255), UNIQUE, NOT NULL)
- `hashed_password` (VARCHAR(255), NOT NULL)
- `full_name` (VARCHAR(255), NOT NULL)
- `role` (VARCHAR(50), NOT NULL) — super_admin, academic_admin, teacher, evaluator, etc.
- `institution_id` (UUID, FK -> institutions.id)
- `is_active` (BOOLEAN, DEFAULT TRUE)
- `created_at` / `updated_at` (TIMESTAMPTZ)

### `exams`
- `id` (UUID, PK)
- `subject_id` (UUID, FK -> subjects.id, NOT NULL)
- `title` (VARCHAR(255), NOT NULL)
- `total_marks` (NUMERIC(5, 2), NOT NULL)
- `passing_marks` (NUMERIC(5, 2), NOT NULL)
- `status` (VARCHAR(50), NOT NULL) — DRAFT, SCHEDULED, ACTIVE, COMPLETED, PUBLISHED
- `created_by` (UUID, FK -> users.id)
- `created_at` (TIMESTAMPTZ)

### `questions`
- `id` (UUID, PK)
- `exam_id` (UUID, FK -> exams.id, NOT NULL)
- `question_number` (VARCHAR(20), NOT NULL)
- `question_text` (TEXT, NOT NULL)
- `max_marks` (NUMERIC(5, 2), NOT NULL)
- `order_index` (INTEGER, NOT NULL)

### `rubric_criteria`
- `id` (UUID, PK)
- `rubric_id` (UUID, FK -> rubrics.id, NOT NULL)
- `description` (TEXT, NOT NULL)
- `max_marks` (NUMERIC(5, 2), NOT NULL)
- `semantic_weight_beta` (NUMERIC(3, 2), DEFAULT 0.65)
- `keywords` (JSONB) — list of essential terms

### `answer_sheets`
- `id` (UUID, PK)
- `exam_id` (UUID, FK -> exams.id, NOT NULL)
- `student_id` (UUID, FK -> students.id)
- `file_path` (VARCHAR(512), NOT NULL)
- `file_hash_sha256` (VARCHAR(64), NOT NULL)
- `status` (VARCHAR(50), NOT NULL) — UPLOADED, OCR_DONE, EVALUATED, PUBLISHED
- `total_pages` (INTEGER, DEFAULT 0)

### `ocr_results`
- `id` (UUID, PK)
- `answer_sheet_id` (UUID, FK -> answer_sheets.id, NOT NULL)
- `page_number` (INTEGER, NOT NULL)
- `raw_text` (TEXT, NOT NULL)
- `confidence_score` (NUMERIC(4, 3))
- `engine` (VARCHAR(50), DEFAULT 'easyocr')
- `bounding_boxes` (JSONB) — [ { id, text, top, left, width, height, conf } ]

### `evaluations`
- `id` (UUID, PK)
- `answer_sheet_id` (UUID, FK -> answer_sheets.id, NOT NULL)
- `question_id` (UUID, FK -> questions.id, NOT NULL)
- `suggested_score` (NUMERIC(5, 2), NOT NULL)
- `final_score` (NUMERIC(5, 2), NOT NULL)
- `teacher_overridden` (BOOLEAN, DEFAULT FALSE)
- `override_reason` (TEXT)
- `evaluated_by_model` (VARCHAR(100), NOT NULL)
- `confidence_score` (NUMERIC(4, 3), NOT NULL)
- `evidence_spans` (JSONB)

### `evaluation_revisions` (Immutable Audit Chain)
- `id` (UUID, PK)
- `evaluation_id` (UUID, FK -> evaluations.id, NOT NULL)
- `revision_number` (INTEGER, NOT NULL)
- `previous_score` (NUMERIC(5, 2))
- `new_score` (NUMERIC(5, 2), NOT NULL)
- `modified_by` (UUID, FK -> users.id, NOT NULL)
- `rationale` (TEXT, NOT NULL)
- `created_at` (TIMESTAMPTZ, NOT NULL)

### `plagiarism_reports` & `plagiarism_similarities`
- Record student pairs, overall similarity score, question-level Jaccard and semantic scores, and matched excerpts with token start/end indices.

### `audit_logs`
- Immutably log every security, authentication, ingestion, OCR, rubric change, score override, and publication event with principal ID, IP address, action, and payload.
