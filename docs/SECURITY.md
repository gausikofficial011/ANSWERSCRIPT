# IntelliGrade — Security Architecture & Governance Standard

**Security Level:** Enterprise Academic Grade  
**Compliance Standards:** OWASP Top 10, FERPA/GDPR Academic Privacy Principles, Immutability Standards

---

## 1. Authentication & Token Lifecycle

- **Password Hashing:** Passwords are encrypted using bcrypt with salt rounds configured to 12.
- **Short-Lived Access Tokens:** JWT access tokens expire after 60 minutes.
- **Refresh Token Rotation:** Refresh tokens expire after 7 days and are hashed and stored in PostgreSQL (`refresh_tokens` table) with revocation on logout.
- **Header Structure:** Tokens are exchanged via standard RFC 6750 `Authorization: Bearer <JWT>` headers.

---

## 2. Server-Side Role-Based Access Control (RBAC)

Permissions are enforced strictly in the backend, independent of frontend routing:
- Dependencies in `app/api/v1/dependencies/auth.py`:
  - `require_auth`: Validates token signature and active user status.
  - `require_teacher`: Restricts access to examination creation, answer sheet upload, and evaluation review.
  - `require_admin`: Restricts access to institutional structure, user management, and system telemetry.
- **Role Permission Matrix:** Defined in `config/permissions.yaml` and verified at startup.

---

## 3. Document Ingestion Security & Path Traversal Prevention

- **MIME & Signature Validation:** Only `application/pdf` with valid `%PDF-` file header signatures are accepted.
- **Filename Sanitization:** Uploaded files are immediately renamed to server-generated UUIDs (`<uuid4>.pdf`).
- **Path Traversal Guards:** File resolution uses strict `Path.resolve()` checks verifying that the resolved path is located strictly within `backend/storage/uploads/`.
- **SHA-256 Content Deduplication:** Exact content hashes are computed to detect duplicate submissions without overwriting existing files.

---

## 4. Academic Privacy & Student Isolation

- **Student Identity Protection:** Students can only query `/results/me` or their own authorized result records.
- **No Peer Script Access:** Students can never access peer submissions, raw OCR transcripts, or teacher-only internal notes.
- **Similarity Anonymization:** In Portal 7, similarity results are labeled as *potential correlation requiring human investigation*, strictly avoiding automated defamatory accusations.

---

## 5. Immutable Audit Trails

Every state modification is logged to the PostgreSQL `audit_logs` table:
- Login attempts (successful and failed).
- Examination creation, question updates, and rubric modifications.
- Answer sheet uploads, OCR reprocessing, and question re-mappings.
- Teacher score overrides (recording previous marks, new marks, and **mandatory rationale**).
- Result publication events.
- Audit records are append-only; database update and delete operations on `audit_logs` are prohibited.
