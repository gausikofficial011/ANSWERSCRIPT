# System Architecture - AI Answer Evaluation System

> [!NOTE]
> This document details the system design, software layers, and tech stack of the AI Answer Evaluation System for MCA Project Submission.

---

## 1. High-Level System Architecture

The AI Answer Evaluation System follows a decoupled, three-tier architecture comprising a modern SPA Frontend, a RESTful API Backend, and a distributed asynchronous Task Worker layer.

```
+-----------------------------------------------------------+
|                        User Interface                     |
|           React SPA (TypeScript + Vite + Vanilla CSS)      |
+-----------------------------------------------------------+
                              |
                     REST API Calls (Axios)
                              v
+-----------------------------------------------------------+
|                         Web Backend                       |
|           FastAPI ASGI (Python 3.11 + SQLAlchemy)          |
+-----------------------------------------------------------+
          |                                       |
     DB Read/Write                           Task Publish
          v                                       v
+-----------------------+              +--------------------+
|   Database Server     |              |    Message Broker  |
|  PostgreSQL 15        |              |    Redis Server    |
+-----------------------+              +--------------------+
                                                  |
                                             Task Consume
                                                  v
                                       +--------------------+
                                       |    Worker Nodes    |
                                       |    Celery Worker   |
                                       +--------------------+
                                                  |
                                             Runs Pipeline
                                                  v
                                       +--------------------+
                                       |    AI Pipeline     |
                                       | EasyOCR / PyTorch  |
                                       | SentenceTransformers|
                                       +--------------------+
```

---

## 2. Component Layout & Tech Stack

### Frontend Tier
* **Language & Framework**: TypeScript, React 18, Vite.
* **State Management**: React Context API (Auth, Notifications).
* **Styling**: Vanilla CSS with custom properties (CSS variables) for full theme control.
* **HTTP Client**: Axios with interceptors for JWT token attachment and token expiry handlers.
* **Iconography**: Lucide React.

### Backend Tier
* **Framework**: FastAPI (ASGI), utilizing standard Pydantic v2 schemas for request validation.
* **ORM & Database**: SQLAlchemy 2.0 (Asyncio) with Alembic migration engine.
* **Security & Auth**: JWT-based stateless authentication, bcrypt password hashing, and endpoint rate limiting.
* **Database**: PostgreSQL 15.

### Background & Worker Tier
* **Task Queue**: Celery.
* **Message Broker**: Redis.
* **Execution Environment**: Celery executes tasks concurrently, using a separate event loop database connection to avoid pool pollution.

### AI Engine Tier
* **OCR Service**: EasyOCR (built on PyTorch) for handwritten text localization and word recognition.
* **PDF Conversion**: `pdf2image` wrapper around Poppler for high-resolution page rendering (200 DPI).
* **Semantic Analysis**: `SentenceTransformers` (`all-MiniLM-L6-v2`) generating 384-dimensional dense vectors for cosine similarity calculation.
* **Keyword Matching**: Tokenizer with NLTK-based stemming and synonym matching dictionaries.
* **Rubric Grading**: Criteria parsing logic matching segments of student text to individual criteria descriptions.
