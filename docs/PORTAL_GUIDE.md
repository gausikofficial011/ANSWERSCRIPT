# IntelliGrade — Comprehensive Ten-Portal User & Operations Guide

**Platform Version:** 1.0.0-rc Enterprise  
**Design System Aesthetic:** Editorial Academic Workspace (Navy / Warm Ivory / Academic Indigo)

---

## Overview of the Ten Dedicated Portals

IntelliGrade provides ten integrated workspaces, each mapped to institutional responsibilities and protected by backend Role-Based Access Control (RBAC):

```
┌────┬──────────────────────────────────┬────────────────────────┬──────────────────────┐
│ #  │ Portal Name                      │ Route                  │ Target Roles         │
├────┼──────────────────────────────────┼────────────────────────┼──────────────────────┤
│ 1  │ Super Admin Control Plane        │ /portals/super-admin   │ super_admin          │
│ 2  │ Academic Administration          │ /portals/academic-admin│ academic_admin       │
│ 3  │ Teacher & Exam Creator           │ /portals/teacher       │ teacher              │
│ 4  │ OCR & Document Review Studio     │ /portals/ocr-review    │ ocr_reviewer, teacher│
│ 5  │ AI Evaluation Diagnostics        │ /portals/ai-evaluation │ ai_evaluator, teacher│
│ 6  │ Evaluator & Moderator Workbench  │ /portals/evaluator     │ evaluator, teacher   │
│ 7  │ Academic Integrity & Collusion   │ /portals/integrity     │ integrity_officer    │
│ 8  │ Student Academic Results         │ /portals/student       │ student              │
│ 9  │ Academic Analytics & QA          │ /portals/analytics     │ qa_analyst, admin    │
│ 10 │ AI Research & Model Lab          │ /portals/research-lab  │ researcher, admin    │
└────┴──────────────────────────────────┴────────────────────────┴──────────────────────┘
```

---

### Portal 1: Super Admin Control Plane
- **Primary Function:** System health oversight, database connectivity, queue telemetry, and security event auditing.
- **Key Capabilities:**
  - Real-time subdaemon telemetry (Uvicorn, PostgreSQL relay, Redis broker, Celery worker pool, Vite server).
  - Physical host memory, CPU logical cores, and storage guardrails.
  - Active execution profile enforcement (`minimal_cpu`).
  - Immutable audit trail search and CSV/JSON export.

### Portal 2: Academic Administration
- **Primary Function:** Curriculum hierarchy, academic calendar, student enrolment, and institutional publication signoffs.
- **Key Capabilities:**
  - Departments & programs directory (CSE, IT, MCA, B.Tech AI&DS).
  - Academic calendar examination scheduling (slots, dates, venues).
  - Bulk student enrolment via CSV with format validation.
  - Institutional publication approvals certifying final grade cards.

### Portal 3: Teacher & Exam Creator
- **Primary Function:** Examination paper authoring, question allocation, model answers, and rubric configuration.
- **Key Capabilities:**
  - Question paper builder with sections, subquestions, and max marks.
  - Model answer configuration and alternative phrasing allowances.
  - Criterion rubric editor with semantic ($\beta$) vs keyword weights.
  - Batch answer script ingestion and sample calibration testing.

### Portal 4: OCR & Document Review Studio
- **Primary Function:** Split-screen document review, PDF rasterisation inspection, and transcript correction.
- **Key Capabilities:**
  - Split-screen workspace: PDF canvas on left; editable transcript on right.
  - Interactive bounding boxes overlay synchronized to extracted text spans.
  - Confidence visualization and error highlighting.
  - Zoom controls (50% to 200%) and 90° clockwise page rotation.
  - Question boundary re-segmentation and multi-page answer continuation markers.

### Portal 5: AI Evaluation Diagnostics
- **Primary Function:** Transparent multi-criterion scoring formulation analysis and evidence grounding.
- **Key Capabilities:**
  - Real-time criterion scoring: $r_c = \beta_c s_c + (1 - \beta_c) k_c$.
  - Interactive semantic weight ratio ($\beta$) calibration slider.
  - Bounded scoring guarantees ($0 \le m \le M_{\max}$).
  - Grounded evidence span references linking student sentences to criteria.
  - Contradiction detection and SymPy symbolic mathematics verification.

### Portal 6: Teacher Evaluator & Moderator Workbench
- **Primary Function:** Human-in-the-loop review, score overrides, and moderation discrepancy resolution.
- **Key Capabilities:**
  - Side-by-side script review: student response vs official model answer standard.
  - One-click approval for high-confidence suggestions ($\ge 82\%$).
  - Teacher score override modal requiring **mandatory written academic rationale**.
  - Immutable revision chain recording previous marks, new marks, and principal ID.

### Portal 7: Academic Integrity & Collusion Studio
- **Primary Function:** Cross-script plagiarism detection and collusion cluster investigation.
- **Key Capabilities:**
  - Pairwise student collusion matrix grid with color-coded similarity cells.
  - MinHash locality-sensitive candidate filtering and n-gram TF-IDF matching.
  - Side-by-side visual excerpt comparison diff highlighting copied passages.
  - Investigation docket for opening and resolving academic misconduct cases.

### Portal 8: Student Academic Results
- **Primary Function:** Privacy-isolated student grade access and certified credential verification.
- **Key Capabilities:**
  - Official certified grade card with final score, percentage, and letter grade.
  - Question-by-question faculty assessment feedback and criterion attainment.
  - Certified PDF result card download.
  - Double-blind re-evaluation appeal submission modal.

### Portal 9: Academic Analytics & Quality Assurance
- **Primary Function:** Psychometric examination analytics and accreditation reporting.
- **Key Capabilities:**
  - Cohort score distribution histogram (variance, mean, median, standard deviation).
  - Question difficulty index ($p = \text{Mean}/\text{Max}$) and discrimination index ($d$).
  - Faculty override frequency tracking and AI-teacher agreement rates ($87.5\%$).
  - Optical character recognition Word Error Rate (WER: $4.0\%$) and Character Error Rate (CER: $0.65\%$).

### Portal 10: AI Research & Model Governance Lab
- **Primary Function:** MLOps command center, local model registry, and dataset manifest management.
- **Key Capabilities:**
  - Host hardware resource telemetry and storage safety guardrails.
  - Academic dataset manifests (Gopika13, IAM, DocLayNet, FUNSD, CROHME, STSb).
  - Model benchmark execution runner and regression metrics history.
  - Lightweight CPU-bounded training pipeline for plagiarism and rubric classifiers.
  - Champion vs challenger model comparison and rollback controls.
