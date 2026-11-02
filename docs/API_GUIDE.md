# IntelliGrade — REST API Reference Guide

**Base URL:** `http://127.0.0.1:8000/api/v1`  
**Authentication:** HTTP Bearer JWT Token (`Authorization: Bearer <token>`)

---

## 1. Authentication Family

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/login` | Authenticate with email/password; returns JWT access token | Public |
| `POST` | `/auth/refresh` | Rotate access token using valid refresh token | Public |
| `GET`  | `/auth/me` | Retrieve authenticated user profile and roles | Authenticated |

---

## 2. Dynamic Portals Configuration

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/portals` | List all 10 role-specific portals, branding tokens, and layouts | Authenticated |
| `GET` | `/portals/{portal_id}` | Granular UI component expectations and workflow states | Authenticated |
| `GET` | `/portals/validation/status` | Real-time Pydantic YAML schema validation summary | Authenticated |

---

## 3. Super Admin & Governance (`/admin`)

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/admin/overview` | Platform health, storage guardrails, host CPU/RAM, daemons | super_admin |
| `GET` | `/admin/queues` | Celery queue monitoring and processed task counts | super_admin |
| `GET` | `/admin/models` | Active model execution profile and model registry | super_admin |

---

## 4. Academic Administration (`/academic`)

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/academic/departments` | Curriculum structure, departments, and academic programs | academic_admin |
| `GET` | `/academic/cohorts` | Enrolled student cohorts, class sections, and faculty advisors | academic_admin |

---

## 5. Subjects & Examination Paper Authoring

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET`  | `/subjects` | List academic subjects with pagination | teacher, admin |
| `POST` | `/subjects` | Create subject code and title | teacher, admin |
| `GET`  | `/exams` | List exams filtered by subject | teacher, admin |
| `POST` | `/exams` | Author exam with title, total marks, and passing threshold | teacher |
| `POST` | `/questions` | Add question with max marks and section index | teacher |
| `POST` | `/rubrics` | Create criterion rubrics with semantic and keyword weights | teacher |

---

## 6. Document Pipeline & OCR Studio

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/answer-sheets/upload` | Multipart PDF upload with SHA-256 duplicate checking | teacher |
| `GET`  | `/answer-sheets/{id}/pages` | List rasterised 200 DPI page images | teacher, ocr |
| `GET`  | `/answer-sheets/{id}/ocr` | Retrieve OCR bounding boxes, text spans, and confidence | teacher, ocr |
| `PATCH`| `/question-mappings/{id}` | Correct or reassign question boundaries | ocr, teacher |

---

## 7. AI Evaluation & Human Review

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/evaluations` | Trigger multi-criterion evaluation on student answers | teacher |
| `GET`  | `/evaluations/{id}` | Inspect criterion breakdown, evidence spans, and marks | evaluator |
| `POST` | `/evaluations/{id}/approve` | Accept proposed marks and advance workflow | evaluator |
| `POST` | `/evaluations/{id}/override` | Execute mark override (**Mandatory rationale required**) | evaluator |
| `GET`  | `/evaluations/{id}/revisions`| Retrieve immutable revision chain for score audit | evaluator, admin |

---

## 8. Academic Integrity & Collusion

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/plagiarism/exams/{id}/analyze` | Trigger pairwise MinHash and n-gram analysis | integrity, teacher |
| `GET`  | `/plagiarism/exams/{id}/matrix` | Retrieve student pairwise collusion matrix grid | integrity, teacher |
| `GET`  | `/plagiarism/reports/{id}` | View side-by-side excerpt diffs of copied passages | integrity, teacher |

---

## 9. Academic Analytics & Quality Assurance

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/analytics/exams/{id}/metrics` | Psychometric distributions, difficulty ($p$) & discrimination ($d$) | qa_analyst, admin |
| `POST`| `/reports/generate` | Generate institutional accreditation PDF / CSV exports | qa_analyst, admin |

---

## 10. AI Research & Model Governance Lab

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET`  | `/research/hardware` | Physical host capacity, logical cores, free disk storage | researcher, admin |
| `GET`  | `/research/benchmarks` | Retrieve latest automated regression benchmark record | researcher, admin |
| `GET`  | `/research/datasets` | Inventory 10 academic datasets and download policies | researcher, admin |
| `POST` | `/research/benchmark` | Dispatch automated hardware benchmark run | researcher, admin |
| `POST` | `/research/train` | Train lightweight CPU-bounded collusion classifier | researcher, admin |
