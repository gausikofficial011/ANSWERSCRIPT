# IntelliGrade: Enterprise Academic Intelligence & Examination Integrity Platform

[![Version](https://img.shields.io/badge/version-1.0.0--rc-indigo.svg)](docs/IMPLEMENTATION_STATUS.md)
[![Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](docs/TESTING.md)
[![Tests](https://img.shields.io/badge/tests-89%20passed-success.svg)](docs/TESTING.md)
[![License](https://img.shields.io/badge/license-Academic%20Enterprise-blue.svg)](config/platform.yaml)
[![Hardware](https://img.shields.io/badge/profile-minimal__cpu-orange.svg)](docs/LOCAL_ML_CAPACITY.md)

> **"AI proposes. Evidence supports. Teachers validate. The system records provenance. Institutions control publication."**

IntelliGrade is a secure, local-first academic assessment and intelligence platform engineered to transform physical examination scripts into verified, transparent, auditable outcomes with zero external paid cloud AI dependencies.

---

## 🌟 Key Capabilities

1. **Ten Role-Specific Operational Portals:** Fully integrated workspaces for Super Admins, Academic Admins, Teachers, OCR Reviewers, AI Evaluators, Faculty Moderators, Integrity Officers, Students, QA Analysts, and ML Researchers.
2. **Signature Split-Screen Review Studio:** Real-time PDF page canvas linked to synchronized OCR bounding boxes, zoom controls, 90° page rotation, and manual transcript correction.
3. **Mathematically Sound Scoring Formulation:** Criterion-level grading $r_c = \beta_c s_c + (1 - \beta_c) k_c$ avoiding double-counting, strictly bounded by question maximum marks, and grounded in extracted evidence spans.
4. **Academic Integrity & Collusion Studio:** Pairwise MinHash candidate retrieval, n-gram TF-IDF matching, interactive collusion matrix grid, and side-by-side excerpt diffs.
5. **Human-in-the-Loop Governance:** Teacher score overrides require **mandatory written academic rationale** logged to an immutable PostgreSQL audit revision chain.
6. **Hardware-Aware Offline Execution:** Automatically profiles host CPU, RAM, and disk storage, enforcing lightweight model profiles (`minimal_cpu`) and disk download guardrails (&ge; 10 GB free space).

---

## 🏛️ The Ten Portals

| Portal | Display Name | Route | Key Capabilities |
| :--- | :--- | :--- | :--- |
| **Portal 1** | [Super Admin Control Plane](docs/PORTAL_GUIDE.md#portal-1-super-admin-control-plane) | `/portals/super-admin` | Subdaemon telemetry, host CPU/RAM/Disk stats, tenant governance |
| **Portal 2** | [Academic Administration](docs/PORTAL_GUIDE.md#portal-2-academic-administration) | `/portals/academic-admin` | Curriculum tree, examination calendar, student cohorts, publication signoff |
| **Portal 3** | [Teacher & Exam Creator](docs/PORTAL_GUIDE.md#portal-3-teacher--exam-creator) | `/portals/teacher` | Question paper builder, model answers, rubric criteria, batch PDF upload |
| **Portal 4** | [OCR & Document Review Studio](docs/PORTAL_GUIDE.md#portal-4-ocr--document-review-studio) | `/portals/ocr-review` | Split-screen canvas, interactive bounding boxes, transcript editor |
| **Portal 5** | [AI Evaluation Diagnostics](docs/PORTAL_GUIDE.md#portal-5-ai-evaluation-diagnostics) | `/portals/ai-evaluation` | Criterion scoring breakdown, live $\beta$ weight slider, evidence spans |
| **Portal 6** | [Teacher Evaluator & Moderator](docs/PORTAL_GUIDE.md#portal-6-teacher-evaluator--moderator-workbench) | `/portals/evaluator` | Side-by-side review, mandatory override reason modal, moderation |
| **Portal 7** | [Academic Integrity & Collusion](docs/PORTAL_GUIDE.md#portal-7-academic-integrity--collusion-studio) | `/portals/integrity` | Interactive pairwise collusion matrix, suspicious cluster discovery, excerpt diffs |
| **Portal 8** | [Student Academic Results](docs/PORTAL_GUIDE.md#portal-8-student-academic-results) | `/portals/student` | Certified grade card, question-wise faculty feedback, appeal request modal |
| **Portal 9** | [Academic Analytics & QA](docs/PORTAL_GUIDE.md#portal-9-academic-analytics--qa) | `/portals/analytics` | Score distribution histogram, difficulty index ($p$), discrimination index ($d$) |
| **Portal 10** | [AI Research & Model Lab](docs/PORTAL_GUIDE.md#portal-10-ai-research--model-governance-lab) | `/portals/research-lab` | Host hardware capacity, dataset manifests, automated benchmark runner |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+ (Python 3.14.6 verified)
- Node.js v20+ / npm v10+
- PostgreSQL 15 & Redis 7 (via WSL2 or native)

### Subsystem Startup Commands

```powershell
# 1. Start WSL Port Forwarder (PostgreSQL 5432 & Redis 6379)
wsl -d Ubuntu -u root /usr/bin/python3 /mnt/c/ANSWERSCRIPT/backend/wsl_port_relay.py

# 2. Run Database Migrations
cd C:\ANSWERSCRIPT\backend
.\.venv\Scripts\python.exe -m alembic upgrade head

# 3. Start Celery Worker Pool
cd C:\ANSWERSCRIPT\backend
.\.venv\Scripts\python.exe -m celery -A app.tasks.celery_app:celery_app worker -l info -Q default,ocr,evaluation,plagiarism,reports,cleanup --pool=solo

# 4. Start FastAPI Application Server (Uvicorn)
cd C:\ANSWERSCRIPT\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 5. Start Vite React 19 Frontend
cd C:\ANSWERSCRIPT\frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

### Seed Credentials
- **Super Administrator:** `admin@amaes.edu` / `Admin@1234`
- **Faculty / Evaluator:** `teacher@amaes.edu` / `Teacher@1234`

---

## 📊 Verified Benchmark Quality Gates

| Benchmark Metric | Quality Gate | Measured Value | Outcome |
| :--- | :--- | :--- | :--- |
| **OCR Word Error Rate (WER)** | $\le 15.0\%$ | **$4.00\%$** | **PASS** |
| **OCR Character Error Rate (CER)**| N/A | **$0.65\%$** | **PASS** |
| **STSb Semantic Similarity** | N/A | MAE **$0.5074$** | **PASS** |
| **Grading Accuracy (MAE)** | $\le 1.25$ marks | **$0.20$ marks** | **PASS** |
| **CPU Model Training Time** | Bounded | **$0.022$ seconds** | **PASS** |

---

## 📚 Complete Technical Documentation

- [System Baseline Audit](docs/BASELINE_AUDIT.md)
- [Local ML Capacity & Hardware Profile](docs/LOCAL_ML_CAPACITY.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Ten-Portal Operations Guide](docs/PORTAL_GUIDE.md)
- [Database Relational Schema](docs/DATABASE_SCHEMA.md)
- [REST API Reference Guide](docs/API_GUIDE.md)
- [AI Model Registry](docs/MODEL_REGISTRY.md)
- [Academic Dataset Catalogue](docs/DATASET_GUIDE.md)
- [Security Architecture](docs/SECURITY.md)
- [Testing & Quality Assurance](docs/TESTING.md)
- [Operations & Troubleshooting](docs/TROUBLESHOOTING.md)
- [Deployment Runbook](docs/DEPLOYMENT.md)
- [Master Implementation Status](docs/IMPLEMENTATION_STATUS.md)
"# ANSWERSCRIPT" 
