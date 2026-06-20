"""
tasks/ — Asynchronous Background Task Layer (Celery)

This layer handles long-running operations asynchronously, preventing
the API from blocking on OCR (up to 30s) and AI evaluation (up to 60s).

Architecture position:
  API Layer ──► Application Use Case ──► Celery Task ──► OCR/AI/Storage
                                         (queued via Redis)

Worker Configuration:
  - Broker:  Redis (redis://redis:6379/0)
  - Backend: Redis (for task result storage)
  - Queues:
      default:     General tasks
      ocr:         OCR processing (CPU-intensive)
      evaluation:  AI evaluation (GPU-optional, CPU-intensive)
      plagiarism:  Plagiarism detection (batch, lower priority)
      reports:     PDF generation
      cleanup:     File lifecycle tasks (lowest priority)

Task Retry Policy (defined per task, not here):
  - Max retries: 3
  - Retry delay: exponential backoff (2^n seconds)
  - Dead letter: failed tasks logged to audit_logs

Contents:
  celery_app.py       — Celery instance, broker/backend config, queue definitions
  ocr_tasks.py        — OCR pipeline task (uploaded → ocr_done)
  evaluation_tasks.py — AI evaluation task (ocr_done → evaluated)
  plagiarism_tasks.py — Plagiarism check task (exam-level, on-demand)
  report_tasks.py     — PDF report generation task (completed → report)
  cleanup_tasks.py    — Scheduled temp file cleanup (cron-style)
"""
