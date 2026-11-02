# User Acceptance Testing (UAT) Report

This report logs UAT scenarios run to verify system usability for teachers and students.

---

## 1. UAT Scenarios

### Scenario 1: Teacher Configures Exam & Rubrics
* **Inputs**: Subject Name = `Mobile Computing`, Questions = Q1-Q5, Rubrics defined with keyword criteria.
* **Expected Result**: Subject and Exam created; database stores question records and relationship mappings.
* **Actual Result**: **Pass**. All tables updated successfully.

### Scenario 2: E2E Answer Sheet Upload & Grading
* **Inputs**: Uploaded handwritten student sheet PDF.
* **Expected Result**: OCR extracts text, maps answers to Q1-Q5, and AI evaluates them.
* **Actual Result**: **Pass**. Upload triggered, Celery processed task, and final results synchronized.

### Scenario 3: Teacher Override Marks
* **Inputs**: Score changed from 4.0 to 6.0 for Q4.
* **Expected Result**: Individual evaluation score updated, final results percentage and grade recalculated.
* **Actual Result**: **Pass**. Overrides saved and aggregates recalculated immediately.
