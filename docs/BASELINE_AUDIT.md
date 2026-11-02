# IntelliGrade — Baseline Repository & System Audit

**Audit Date:** 2026-10-26  
**Auditor:** IntelliGrade Autonomous Principal Engineering Team  
**Platform Version:** IntelliGrade Enterprise 1.0.0-rc  
**Audit Purpose:** Comprehensive inspection of existing codebase, dependencies, test baseline, hardware environment, and architecture readiness prior to full multi-portal enterprise implementation.

---

## 1. Executive Summary

IntelliGrade is an enterprise-grade, local-first academic assessment and intelligence platform engineered to transform handwritten/printed examination scripts into verified, transparent, auditable academic outcomes. 

The core end-to-end evaluation pipeline—consisting of PDF rasterisation via `pypdfium2`, handwriting recognition via `EasyOCR`, question boundary segmentation, hybrid semantic-lexical scoring via `SentenceTransformers` and `Scikit-Learn`, teacher verification with mandatory rationale, and publication controls—has been verified as operational in the local development environment.

This audit establishes the baseline metrics, identified technical debt, hardware constraints, and the roadmap for completing all 10 role-specific operational portals and YAML-driven governance.

---

## 2. Environment & Hardware Diagnostics

Hardware inspection executed via native Windows kernel API (`scripts/inspect_hardware.py`):

| Diagnostic Parameter | Detected Value | Implications / Guardrails |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 AMD64 (10.0.26300) | Native PowerShell runtime with WSL2 relay for Linux-native daemons. |
| **Python Runtime** | Python 3.14.6 (64-bit) | Modern language features enabled; C-extensions must be pre-compiled. |
| **Node.js / npm** | Node v20+ / npm v10+ | React 19 + TypeScript 5.8 + Vite 6.2 modern tooling. |
| **CPU Architecture** | 12 Logical Cores | Multi-threaded background tasks supported; Celery concurrency tuned to 4 workers. |
| **System RAM** | 15.70 GB Total (~1.1 GB Free) | **Critical memory constraint**: Heavyweight model caching must be shared per process. |
| **Available Storage** | 16.53 GB Free of 474.72 GB | **Strict disk constraint**: Multi-GB raw dataset downloads must be prevented; manifests and local synthetic samples required. |
| **Acceleration (PyTorch)**| PyTorch 2.12.1+cpu (`CUDA: False`)| Model profile set to `minimal_cpu` / `balanced_cpu`. Inference prioritises 80MB MiniLM and quantized ONNX/CPU weights. |
| **Hugging Face Cache** | `paraphrase-multilingual-mpnet-base-v2` | Cached locally; ready for immediate semantic embeddings. |
| **EasyOCR Cache** | Craft detector + English Latin CRNN | Cached locally; ready for offline inference. |

---

## 3. Architecture & Service Status

The system operates four integrated daemons:

```
[ Frontend: React 19 + Vite ] (Port 5173)
             │
             ▼ REST API / WebSocket
[ Backend: FastAPI + Pydantic v2 ] (Port 8000)
       │                 │
       ▼ asyncpg         ▼ celery / redis
[ PostgreSQL 15 ]   [ Redis 7.0 ]
 (WSL Port 5433 ->   (WSL Port 6380 ->
  Host 5432)          Host 6379)
                         │
                         ▼
             [ Celery Worker Pool ]
   (Queues: default, ocr, evaluation, plagiarism, reports, cleanup)
```

1. **Port Relay Daemon (`wsl_port_relay.py`)**: Forwards PostgreSQL (5433 -> 5432) and Redis (6380 -> 6379) reliably across the Windows-WSL boundary without Hyper-V vEthernet SSL/firewall drops.
2. **FastAPI Application Server**: Uvicorn running asynchronous endpoints with JWT auth, structured audit logging, and Pydantic schema validation.
3. **Celery Worker**: Configured with dedicated queues (`default`, `ocr`, `evaluation`, `plagiarism`, `reports`, `cleanup`).
4. **Vite Development Server**: Hot-module reloading server delivering React 19 SPA.

---

## 4. Existing Database Baseline

The PostgreSQL database maintains 28 core domain tables:
- **Core Entities:** `users`, `institutions`, `departments`, `programs`, `classes`, `subjects`
- **Assessment Engine:** `exams`, `questions`, `model_answers`, `rubrics`, `rubric_criteria`
- **Document Pipeline:** `answer_sheets`, `answer_sheet_pages`, `ocr_results`, `ocr_regions`, `question_mappings`
- **Evaluation & Review:** `evaluations`, `criterion_evaluations`, `evidence_references`, `evaluation_revisions`, `review_assignments`
- **Integrity & Results:** `plagiarism_reports`, `plagiarism_similarities`, `final_results`, `result_publications`
- **Governance:** `audit_logs`, `processing_jobs`, `notifications`

**Default Seeded Principals:**
- Super Admin: `admin@amaes.edu`
- Teacher: `teacher@amaes.edu`
- System Daemon: `system@eval.internal` (`00000000-0000-0000-0000-000000000000`)

---

## 5. Existing Test Baseline

1. **Unit Test Suite (`pytest backend/tests/unit`)**:
   - 75 tests passing: Auth, security hashing, OCR rasterisation, segmentation rules, scoring bounds, rubric weighting, plagiarism math, audit immutability, revision history.
2. **Infrastructure Test Suite (`pytest backend/tests/infrastructure`)**:
   - 13 tests passing: Celery task dispatch, Redis pub/sub, database connection pooling, file upload security, path traversal prevention.
3. **End-to-End Live Workflow**:
   - `backend/scripts/complete_demo_workflow.py` executed successfully through full pipeline: Exam setup -> PDF generation -> Page rasterisation -> EasyOCR extraction -> Question mapping -> Semantic evaluation -> Teacher override -> Publication.
4. **Frontend Production Build**:
   - `tsc -b && vite build` passing: 1,855 modules compiled into optimized chunks with zero TypeScript errors.

---

## 6. Technical Debt & Deficiencies Identified

Prior to this implementation phase, the following gaps existed:
1. **Multi-Portal Experience**: The UI only exposed a unified teacher/admin dashboard. Portals for Super Admin, Academic Administration, OCR Document Review, AI Evaluation Diagnostics, Integrity Collusion Matrix, Student Results, Analytics, and Model Research Lab were not cleanly differentiated.
2. **Declarative YAML Hierarchy**: Configuration existed in Python files and environment variables, but lacked a formal validated hierarchy in `config/` (platform, permissions, models, datasets, portals, features) with startup schema enforcement.
3. **Hardware-Aware Model Profiles**: Model downloading did not check available disk space or RAM against hardware capacity before loading weights.
4. **Plagiarism Collusion Matrix**: While pairwise similarity algorithms existed in the backend, there was no interactive visual matrix view for cohorts.
5. **OCR Split-Screen Overlay**: The review interface displayed text transcripts but lacked a synchronized SVG/canvas bounding-box overlay linking document image coordinates to OCR text spans.

---

## 7. Implementation Plan

The following phases will be executed systematically:
1. **Phase 1: Baseline Audit & Capacity Documentation** (Completed).
2. **Phase 2: YAML Configuration Architecture & Backend Validator**: Establish `config/` structure with Pydantic startup validation and API exposure.
3. **Phase 3: Dataset Registry & Local ML Infrastructure**: Build dataset manifests, hardware-bounded benchmark scripts, and small model training pipelines.
4. **Phase 4: Backend API Extensions**: Add endpoints for all 10 portals (admin telemetry, academic cohorts, OCR bounding boxes, integrity matrix, analytics, research benchmarks).
5. **Phase 5: Premium Design System & 10 Role Portals**: Build `PortalShell` and all 10 responsive portal workspaces in React/TypeScript with the requested academic editorial aesthetic.
6. **Phase 6: Verification & Testing**: Run unit tests, frontend build, and browser automation to verify end-to-end functionality.
7. **Phase 7: Full Documentation Suite**: Deliver complete architectural and operational guides.
