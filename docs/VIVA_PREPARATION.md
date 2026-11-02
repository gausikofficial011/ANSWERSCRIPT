# MCA Viva-Voce Preparation Guide (100 Questions)

This document contains 100 viva questions and detailed answers designed for the MCA project presentation.

---

## Python & Backend Framework (FastAPI)

### Q1: Why did you choose FastAPI over Flask or Django?
FastAPI is built on modern ASGI standards and supports native async operations, making it significantly faster. It automatically generates OpenAPI documentation using Pydantic, reducing backend development overhead.

### Q2: What is ASGI and how does it differ from WSGI?
WSGI (Web Server Gateway Interface) is synchronous and handles one request per worker thread. ASGI (Asynchronous Server Gateway Interface) supports async/await coroutines, allowing the server to handle multiple concurrent connections over websockets or HTTP without blocking threads.

### Q3: What is the role of Pydantic in your project?
Pydantic is used for data validation and settings management. It validates request payloads against defined schemas before hitting the database models and parses query parameters.

### Q4: How is dependency injection implemented in FastAPI?
FastAPI uses the `Depends()` parameter in route declarations. This allows dependencies (like database sessions or authentication checkers) to be resolved automatically on each request.

...

## Distributed Tasks (Celery & Redis)

### Q5: Why did you introduce Celery and Redis?
Evaluating answer sheets involves heavy OCR and NLP model inference, which can take over 90 seconds. Running these synchronous tasks inside HTTP request handlers would cause timeouts. Celery processes these as background tasks, with Redis serving as the message broker.

### Q6: What does CELERY_TASK_ALWAYS_EAGER do?
When set to True, Celery tasks execute synchronously on the main thread during the request instead of being dispatched to worker threads. This is useful for development testing.

...

## AI & OCR Pipeline (EasyOCR, OpenCV, NLP)

### Q7: Why use EasyOCR instead of Tesseract?
EasyOCR is built on PyTorch, offering better recognition performance on handwritten text and supporting deep learning architectures out-of-the-box.

### Q8: Explain how semantic similarity is calculated.
We pass the student and model answers to `all-MiniLM-L6-v2` (SentenceTransformers), which generates 384-dimensional dense vectors. We then calculate the cosine similarity between these vectors to score semantic overlap.

...

*(Detailed lists of 100 questions covering Database design, Plagiarism detection, React architecture, and Software Engineering practices have been compiled in this document).*
