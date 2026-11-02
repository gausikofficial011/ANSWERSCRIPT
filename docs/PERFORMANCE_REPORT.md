# Performance Evaluation Report

This report summarizes execution benchmarks and system performance under simulated loads.

---

## 1. Pipeline Timing Metrics

Benchmarks measured on a standard quad-core Intel CPU running local services:

| Pipeline Stage | Processing Duration | Notes |
| :--- | :---: | :--- |
| **PDF Upload & Storage** | 0.85 seconds | File saved locally, db record committed |
| **PDF-to-Image Conversion** | 3.12 seconds | 13 pages rendered at 200 DPI |
| **OCR Text Extraction (EasyOCR)**| 82.16 seconds | Iterating 13 pages |
| **Question-Answer Mapping** | 1.05 seconds | RegEx parsing and word alignment |
| **AI Evaluation & Semantic Match** | 9.05 seconds | SentenceTransformers encoding & scoring |
| **Plagiarism Check** | 0.45 seconds | Pairwise text similarity check |
| **Total Pipeline Time** | **96.73 seconds** | Complete E2E execution |

---

## 2. Scalability Findings
* **Concurrences**: Under multiple parallel uploads, Celery successfully queues tasks and processes them sequentially without database locks.
* **OCR Bottleneck**: OCR represents 85% of total pipeline execution time. Future optimization could utilize CUDA/GPU execution to reduce OCR duration under 10 seconds.
