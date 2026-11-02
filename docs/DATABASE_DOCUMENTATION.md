# Database Schema Documentation

This document describes the PostgreSQL relational database design.

---

## 1. Database Table Catalog

### `users`
* `id` (UUID, Primary Key)
* `username` (VARCHAR, Unique)
* `email` (VARCHAR, Unique)
* `password_hash` (VARCHAR)
* `role` (VARCHAR: `admin`, `teacher`)

### `answer_sheets`
* `id` (UUID, Primary Key)
* `exam_id` (UUID, Foreign Key -> `exams.id`)
* `student_id` (UUID, Foreign Key -> `students.id`)
* `status` (VARCHAR: `UPLOADED`, `QUEUED_FOR_OCR`, `TEACHER_REVIEW_PENDING`, `VERIFIED`, etc.)
* `page_count` (INTEGER)
* `file_path` (VARCHAR)
* `plagiarism_flagged` (BOOLEAN)
* `processing_started_at` (TIMESTAMP)
* `processing_completed_at` (TIMESTAMP)

### `ocr_results`
* `id` (UUID, PK)
* `answer_sheet_id` (UUID, FK -> `answer_sheets.id`)
* `page_number` (INTEGER)
* `extracted_text` (TEXT)
* `confidence_score` (FLOAT)

### `evaluations`
* `id` (UUID, PK)
* `answer_sheet_id` (UUID, FK -> `answer_sheets.id`)
* `question_id` (UUID, FK -> `questions.id`)
* `awarded_marks` (FLOAT)
* `semantic_similarity_score` (FLOAT)
* `keyword_score` (FLOAT)
* `rubric_score` (FLOAT)
* `feedback` (TEXT)
* `verification_status` (VARCHAR: `PENDING`, `VERIFIED`)

### `final_results`
* `id` (UUID, PK)
* `exam_id` (UUID, FK -> `exams.id`)
* `student_id` (UUID, FK -> `students.id`)
* `answer_sheet_id` (UUID, FK -> `answer_sheets.id`)
* `total_marks_obtained` (FLOAT)
* `percentage` (FLOAT)
* `grade` (VARCHAR)
* `pass_fail_status` (VARCHAR)

---

## 2. Table Relationships

```
+-----------+         +-----------+         +------------------+
|  Subject  | 1 --- * |   Exam    | 1 --- * |   Answer Sheet   |
+-----------+         +-----------+         +------------------+
                            |                        | 1
                            |                        |
                            |                        +-- * [OCR Results]
                            |                        |
                            | 1                      +-- * [Evaluations]
                            v                        |
                      +-----------+                  v
                      | Questions | 1 ------------ * [Mappings]
                      +-----------+
```
