# Final Production Deployment Checklist

Pre-flight checklist before launching the system in production:

* **[ ] Database Migrations**: Run `alembic upgrade head` to configure tables.
* **[ ] Security Keys**: Update `JWT_SECRET_KEY` in `.env` to a secure 32-byte hash.
* **[ ] CORS Settings**: Restrict `allow_origins` in `main.py` to the production domain.
* **[ ] Celery Configuration**: Ensure `CELERY_TASK_ALWAYS_EAGER` is set to `False` so task workers run asynchronously.
* **[ ] GPU Acceleration**: Verify PyTorch is configured with CUDA drivers on the server to accelerate OCR processing.
* **[ ] PM2 Process Manager**: Setup PM2 config to monitor uvicorn and celery worker processes.
