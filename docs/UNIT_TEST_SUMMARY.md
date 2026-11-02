# Unit Test Summary - AI Answer Evaluation System

This document summarizes the unit test suites written for testing backend components.

---

## 1. Test Suite Coverage

| Test Module | Coverage Area | Status |
| :--- | :--- | :---: |
| `test_ocr_use_cases.py` | OCR processing pipeline triggers, state machines | **PASSED** |
| `test_results_use_cases.py` | Grade boundaries, percentages, pass/fail status calculations | **PASSED** |
| `test_upload_answer_sheet.py` | File validation, malware scans, student mapping overrides | **PASSED** |
| `test_evaluation_use_cases.py` | Criteria-based grading, similarity computations, overrides | **PASSED** |
| `test_plagiarism_use_cases.py` | Text similarity analysis, pairwise checking, flagging | **PASSED** |

---

## 2. Test Execution Command
To run unit tests:
```bash
cd backend
.venv/Scripts/pytest tests/unit/
```
