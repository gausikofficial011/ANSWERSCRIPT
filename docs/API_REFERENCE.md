# API Reference Guide - AI Answer Evaluation System

This document catalogs every API endpoint available in the FastAPI backend.

---

## 1. Authentication Router (`/api/v1/auth`)

* **`POST /login`**
  - *Description*: Authenticate user and return JWT tokens.
  - *Payload*: `{"username": "...", "password": "..."}`
  - *Response*: `{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}`

* **`POST /register`**
  - *Description*: Register a new teacher profile.
  - *Payload*: `{"username": "...", "password": "...", "email": "...", "full_name": "..."}`

---

## 2. Subjects Router (`/api/v1/subjects`)

* **`GET /`**: List all subjects (paginated).
* **`POST /`**: Create a subject.
* **`GET /{id}`**: Get subject details.
* **`PUT /{id}`**: Update subject.
* **`DELETE /{id}`**: Delete subject.

---

## 3. Exams Router (`/api/v1/exams`)

* **`POST /`**: Create an exam.
* **`GET /{id}`**: Get exam details.
* **`PUT /{id}`**: Update exam status (Draft/Active/Closed).

---

## 4. Answer Sheets Router (`/api/v1/answer-sheets`)

* **`POST /upload`**
  - *Description*: Upload handwritten answer sheet PDFs.
  - *Payload*: Multipart Form data containing `exam_id`, `files` (array of PDF files).
  - *Response*: Array of enqueued upload details.

* **`GET /{id}`**: Get answer sheet processing status.

---

## 5. Overview Dashboard Router (`/api/v1/results`)

* **`GET /overview`**
  - *Description*: Return high-level E2E pipeline statistics.
  - *Response*:
    ```json
    {
      "total_answer_sheets": 12,
      "pending_ocr": 0,
      "pending_evaluation": 0,
      "completed_evaluations": 12,
      "teacher_review_pending": 1,
      "plagiarism_alerts": 0,
      "average_score": 74.5,
      "average_processing_time": 95.2
    }
    ```
