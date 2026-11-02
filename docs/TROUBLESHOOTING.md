# IntelliGrade — Operations & Troubleshooting Guide

**Platform:** Windows 11 AMD64 (Native PowerShell + WSL2 Linux Services)

---

## 1. Port Forwarding & WSL2 Network Relay

### Symptom: `asyncpg.exceptions.ConnectionDoesNotExistError` or Connection Timed Out
- **Root Cause:** On Windows with WSL2, Hyper-V virtual Ethernet switches dynamically reassign IP addresses upon reboot, causing Windows host processes to lose connection to Linux PostgreSQL (port 5432) or Redis (port 6379).
- **Verified Solution:** IntelliGrade runs a native bidirectional socket forwarder: `backend/wsl_port_relay.py`.
- **Command to verify or restart port relay:**
  ```powershell
  wsl -d Ubuntu -u root /usr/bin/python3 /mnt/c/ANSWERSCRIPT/backend/wsl_port_relay.py
  ```
  This relays Linux PostgreSQL (5433 -> 5432) and Redis (6380 -> 6379) directly to `127.0.0.1`.

---

## 2. Celery Worker Concurrency on Windows

### Symptom: `ValueError: not enough values to unpack (expected 3, got 0)` or process hang
- **Root Cause:** Python multiprocessing under Windows defaults to `spawn`, which can deadlock when Celery uses the default prefork pool with PyTorch C-extensions.
- **Verified Solution:** Always execute Celery on Windows with `--pool=solo`:
  ```powershell
  cd C:\ANSWERSCRIPT\backend
  .\.venv\Scripts\python.exe -m celery -A app.tasks.celery_app:celery_app worker -l info -Q default,ocr,evaluation,plagiarism,reports,cleanup --pool=solo
  ```

---

## 3. Storage Quota Alerts

### Symptom: `Dataset download blocked by storage safety policy`
- **Root Cause:** Host system has bounded free storage (e.g. 16.9 GB free).
- **Verified Solution:** IntelliGrade enforces a 10.0 GB free disk guardrail. High-volume datasets (DocLayNet, PubLayNet) are retained as remote manifests. To benchmark without downloading large archives, use the cached fixtures in `ml/datasets/processed/`.
