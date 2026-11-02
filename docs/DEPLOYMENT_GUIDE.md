# Deployment Guide - AI Answer Evaluation System

This guide outlines setup instructions for local development and production environments.

---

## 1. Prerequisites & Environment

### Hardware Requirements
* **CPU**: Quad-core 2.4 GHz minimum.
* **RAM**: 8 GB (16 GB recommended for running PyTorch models).
* **Storage**: 10 GB free space.

### Software Prerequisites
* **Operating System**: Windows 10/11 or Ubuntu 20.04+.
* **Python**: v3.11
* **Node.js**: v18+
* **PostgreSQL**: v15
* **Redis**: v6+
* **Poppler**: Required for PDF rendering.

---

## 2. Installation & Configuration

### Step 1: Poppler Setup
* **Windows**: Download poppler-windows, extract to a folder, and add the `bin/` directory to the system environment PATH variables.
* **Ubuntu**: Run `sudo apt-get install -y poppler-utils`.

### Step 2: Database Setup
1. Open PostgreSQL CLI or pgAdmin and run:
   ```sql
   CREATE DATABASE answer_evaluation;
   CREATE USER postgres WITH PASSWORD 'postgres';
   GRANT ALL PRIVILEGES ON DATABASE answer_evaluation TO postgres;
   ```

### Step 3: Backend Installation
1. Navigate to the backend directory:
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate   # On Windows
   source .venv/bin/activate  # On Linux/macOS
   pip install -r requirements.txt
   ```
2. Configure the `.env` file:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/answer_evaluation
   JWT_SECRET_KEY=super_secret_key_change_me
   REDIS_URL=redis://localhost:6379/0
   CELERY_TASK_ALWAYS_EAGER=False
   ```
3. Run Alembic migrations:
   ```bash
   alembic upgrade head
   ```
4. Seed admin/teacher profiles:
   ```bash
   python setup_db.py
   ```

### Step 4: Frontend Installation
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   npm install
   ```
2. Configure `.env`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

---

## 3. Running the Application

### Start Backend Services
1. Run Redis server.
2. Start Celery worker in backend directory:
   ```bash
   celery -A app.core.celery_app worker --loglevel=info
   ```
3. Start FastAPI server:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

### Start Frontend Server
1. Navigate to frontend directory and run:
   ```bash
   npm run dev
   ```
2. Open browser at `http://localhost:5173`.
