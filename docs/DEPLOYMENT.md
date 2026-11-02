# IntelliGrade — Deployment & Operations Runbook

**Target Environment:** Local-First Academic Server / Workstation (Windows 11)  
**Port Allocations:**
- Frontend: `http://127.0.0.1:5173`
- Backend API: `http://127.0.0.1:8000`
- PostgreSQL: `127.0.0.1:5432`
- Redis: `127.0.0.1:6379`

---

## 1. Prerequisites Checklist

1. Python 3.11+ (Python 3.14.6 verified)
2. Node.js v20+ / npm v10+
3. PostgreSQL 15 & Redis 7 (installed via WSL2 Ubuntu)
4. Hardware: Minimum 8 GB RAM, &ge; 15 GB Free Disk Space

---

## 2. Production / Local Startup Sequence

Execute the following commands in separate terminals:

### Step 1: Start WSL Network Port Relay (Postgres & Redis)
```powershell
wsl -d Ubuntu -u root /usr/bin/python3 /mnt/c/ANSWERSCRIPT/backend/wsl_port_relay.py
```

### Step 2: Run Database Migrations
```powershell
cd C:\ANSWERSCRIPT\backend
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### Step 3: Start Celery Background Worker Pool
```powershell
cd C:\ANSWERSCRIPT\backend
.\.venv\Scripts\python.exe -m celery -A app.tasks.celery_app:celery_app worker -l info -Q default,ocr,evaluation,plagiarism,reports,cleanup --pool=solo
```

### Step 4: Start FastAPI Application Server (Uvicorn)
```powershell
cd C:\ANSWERSCRIPT\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Step 5: Start React 19 Frontend (Vite)
```powershell
cd C:\ANSWERSCRIPT\frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

---

## 3. Seed Credentials

- **Super Administrator:** `admin@amaes.edu` / `Admin@1234`
- **Faculty / Evaluator:** `teacher@amaes.edu` / `Teacher@1234`
- **System Daemon:** `system@eval.internal` (`00000000-0000-0000-0000-000000000000`)
