# Workflow Documentation - AI Answer Evaluation System

This document outlines the operational workflows for the different user roles in the system.

---

## 1. Teacher Workflow

The primary administrative and evaluation workflow follows these steps:

```
[Teacher Login]
      |
      v
[Configure Subject & Exam Parameters]
      |
      v
[Define Model Answers & Rubrics]
      |
      v
[Upload Student Answer Sheets (PDF)] ---> (AI Pipeline Synchronous/Asynchronous)
      |
      v
[Review OCR & Question Mappings]
      |
      v
[Review AI Graded Sheets & Overrides]
      v
[Publish Results & Export PDF Reports]
```

### Key Steps:
1. **Syllabus Configuration**: Create a Subject (e.g., `MCWN-TEST-22`) and an Exam.
2. **Key Definition**: Add questions, types (Short/Long), maximum marks, model answers, and expected keywords.
3. **Criteria-based Rubrics**: Define rubric sheets for each question, mapping maximum marks to specific semantic criteria.
4. **Answer Sheet Upload**: Upload student handwritten answer sheets (single/multiple PDFs).
5. **Human-in-the-Loop Override**: Review AI-assigned scores, view semantic explanations, and optionally override marks before publishing.

---

## 2. Student Workflow

The student interface is read-only and designed for transparent feedback:
1. **Student Login**: Authenticate with credentials.
2. **Overview Dashboard**: View grades, pass/fail status, and average marks across exams.
3. **View Graded Script**: Open the evaluated answer sheet page to view side-by-side annotations showing:
   - Extracted OCR text per page.
   - Awarded marks per question.
   - Keyword match highlights and AI explanations.

---

## 3. Plagiarism Detection Workflow

1. **Auto-Trigger**: Executes automatically after all exam answer sheets are evaluated.
2. **Text Comparison**: Performs pairwise comparisons between student answer texts.
3. **Similarity Threshold**: Flag matches exceeding the suspicious threshold (default: 60%).
4. **Review Dashboard**: Displays overlapping segments side-by-side. The teacher confirms or dismisses the plagiarism alert.
