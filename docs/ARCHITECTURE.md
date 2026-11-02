# IntelliGrade — System Architecture & Technical Specification

**Document Version:** 2.1.0-Enterprise  
**Classification:** Academic Engineering Specification  
**Architecture Paradigm:** Local-First, Offline-Capable Multi-Tier Assessment Platform

---

## 1. Architectural Philosophy

IntelliGrade is engineered around a core academic governance principle:

> **"AI proposes. Evidence supports. Teachers validate. The system records provenance. Institutions control publication."**

The platform operates 100% locally on standard academic hardware without reliance on external paid LLM APIs or proprietary cloud subscriptions.

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                       INTELLIGRADE SYSTEM ARCHITECTURE                         │
└────────────────────────────────────────────────────────────────────────────────┘

  [ Client Tier: React 19 + TypeScript + Vite ] (Port 5173)
  ├── Unified PortalShell: Navigation, Theme Tokens, Breadcrumbs, Status Pill
  └── 10 Role-Specific Portals:
      ├── P1: Super Admin Control Plane
      ├── P2: Academic Administration
      ├── P3: Teacher & Exam Creator
      ├── P4: OCR & Document Review Studio (Split-Screen Canvas)
      ├── P5: AI Evaluation Diagnostics (Multi-Criterion r_c Engine)
      ├── P6: Teacher Evaluator & Moderator Workbench
      ├── P7: Academic Integrity & Collusion Studio (Matrix)
      ├── P8: Student Academic Results Portal
      ├── P9: Academic Analytics & Quality Assurance (Psychometrics)
      └── P10: AI Research & Model Governance Lab (MLOps)
                               │
                               ▼ REST API (JWT Authenticated)
  [ Application Tier: FastAPI + Pydantic v2 ] (Port 8000)
  ├── Clean Architecture (Domain -> Application -> Infrastructure)
  ├── YAML Configuration Hierarchy Validator (Pydantic Startup Enforcement)
  ├── Bounded Scoring Policy Enforcement Engine (r_c = beta*s_c + (1-beta)*k_c)
  ├── MinHash Locality-Sensitive Hashing & Collusion Matrix Engine
  └── Immutable Audit Logger & Revision Chain
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
  [ PostgreSQL 15 Relational DB ]     [ Redis 7.0 In-Memory Broker ]
  ├── 28 Relational Domain Tables      ├── Dedicated Celery Queues:
  ├── Tenant & Faculty Scoping         │   ├── `ocr` (180s limit)
  ├── JSONB Coordinates & Geometry     │   ├── `evaluation` (120s limit)
  └── Immutable Audit Event Store      │   ├── `plagiarism` (180s limit)
                                       │   ├── `reports` (60s limit)
                                       │   └── `cleanup` (30s limit)
                                       ▼
                         [ Celery Worker Pool (Pool: Solo) ]
                         ├── Document Rasteriser (pypdfium2 @ 200 DPI)
                         ├── OCR Handwriting Engine (EasyOCR Latin CRNN)
                         ├── Embedding Inference (all-MiniLM-L6-v2 / mpnet)
                         ├── Scikit-Learn Collusion Classifier (joblib)
                         └── SymPy Symbolic Mathematics Verifier
```

---

## 2. Mathematical Scoring Pipeline Specification

To prevent double-counting between semantic embedding similarity and keyword matching, IntelliGrade computes scores at the rubric criterion level:

For each criterion $c \in \{1, \dots, K\}$:

$$r_c = \beta_c \cdot s_c + (1 - \beta_c) \cdot k_c$$

where:
- $s_c \in [0, 1]$ is calibrated cosine similarity of sentence embeddings for criterion $c$.
- $k_c \in [0, 1]$ is criterion-specific concept and keyword coverage ratio.
- $\beta_c \in [0.20, 0.85]$ is the criterion semantic weight (default: $0.65$).
- The criterion mark awarded is:

$$m_c = M_c \cdot r_c$$

- The total question score is bounded strictly by the question maximum:

$$M_{\text{suggested}} = \min\left(M_{\max}, \max\left(0, \sum_{c=1}^K m_c\right)\right)$$

This mathematical formulation guarantees:
1. $0 \le M_{\text{suggested}} \le M_{\max}$.
2. Repetition and keyword stuffing cannot artificially inflate marks without semantic grounding.
3. Every mark awarded corresponds to verifiable evidence spans in the student script.

---

## 3. Storage Hierarchy & Local File System

```
storage/
├── uploads/              # Raw ingested PDFs (SHA-256 hashed, tenant scoped)
├── pages/                # Rasterised 200 DPI PNG images (page-level cache)
├── reports/              # Certified PDF result cards and accreditation exports
└── ml/
    ├── models/           # Local model checkpoints (e.g., plagiarism_v1.joblib)
    ├── datasets/
    │   ├── raw/          # Unpacked academic dataset samples
    │   ├── processed/    # Normalized benchmark fixtures (JSON)
    │   └── manifests/    # SHA-256 checksum catalogs for large archives
    └── benchmarks/       # Automated regression test records
```
