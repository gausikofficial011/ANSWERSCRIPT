# IntelliGrade — Local Machine Learning Capacity & Hardware Profile

**Profile Date:** 2026-10-26  
**Auditor:** IntelliGrade Autonomous MLOps & Hardware Engineering Team  
**Runtime Execution Target:** Local-First Offline Assessment (Zero Cloud AI API Dependency)

---

## 1. Physical Hardware Diagnostic Snapshot

| Parameter | Detected Value | Operational Threshold / Constraint |
| :--- | :--- | :--- |
| **System Architecture** | AMD64 (x86_64) | 64-bit instruction set with AVX2 support |
| **CPU Logical Cores** | 12 Logical Cores | Parallel multiprocessing for OCR batching & tokenization |
| **Host System RAM** | 15.70 GB Total | ~1.1 GB Currently Free (Dynamic Windows memory allocation) |
| **Primary Storage** | 474.72 GB Total | **16.53 GB Free Disk Space** (Strict storage budget) |
| **GPU / Acceleration** | CPU Only (`CUDA: False`) | PyTorch CPU runtime; FP32 / INT8 quantized inference |
| **Operating System** | Microsoft Windows 11 | Windows NT Kernel 10.0.26300 |
| **Python Version** | 3.14.6 64-bit | Modern GIL optimizations and fast async I/O |

---

## 2. Hardware-Aware Model Execution Profiles

To prevent out-of-memory (OOM) crashes and disk exhaustion on this host, IntelliGrade enforces strict model execution profiles:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MODEL PROFILES MATRIX                           │
├─────────────────────┬──────────────┬──────────────┬────────────────────┤
│ Profile             │ RAM Footprint│ Disk Required│ Supported Engines  │
├─────────────────────┼──────────────┼──────────────┼────────────────────┤
│ minimal_cpu         │ < 1.2 GB     │ < 500 MB     │ EasyOCR (EN),      │
│ (Active Default)    │              │              │ all-MiniLM-L6-v2,  │
│                     │              │              │ TF-IDF, LogReg     │
├─────────────────────┼──────────────┼──────────────┼────────────────────┤
│ balanced_cpu        │ 1.5 - 2.5 GB │ 500 MB - 2 GB│ mpnet-base-v2,     │
│ (Permitted Batch)   │              │              │ EasyOCR Craft,     │
│                     │              │              │ Scikit-Learn GBM   │
├─────────────────────┼──────────────┼──────────────┼────────────────────┤
│ gpu_accelerated     │ 4.0 - 8.0 GB │ 2 GB - 10 GB │ TrOCR, LayoutLMv3  │
│ (Disabled on Host)  │              │              │ CUDA FP16          │
├─────────────────────┼──────────────┼──────────────┼────────────────────┤
│ research_exp        │ > 8.0 GB     │ > 10 GB      │ Full LLM/VLM,      │
│ (Simulated/Bench)   │              │              │ 7B Parameter models│
└─────────────────────┴──────────────┴──────────────┴────────────────────┘
```

### Active Profile: `minimal_cpu`
- **OCR Engine:** EasyOCR English Latin CRNN model with Craft text detector (~120 MB RAM, already cached locally in `~/.EasyOCR/`).
- **Semantic Embeddings:** `all-MiniLM-L6-v2` (80 MB disk, 384 dimensions, ~150 MB RAM) or the already-cached `paraphrase-multilingual-mpnet-base-v2` (768 dimensions, ~420 MB RAM).
- **Plagiarism & Integrity:** Locality-Sensitive Hashing (MinHash), TF-IDF word & character n-grams, and Scikit-Learn Logistic Regression (~30 MB RAM).
- **Mathematical Evaluation:** SymPy symbolic algebra + NumPy unit tolerance verification (zero neural overhead).

---

## 3. Storage Budget & Download Safeguards

With **16.53 GB free disk space**, downloading multi-gigabyte research datasets (such as 100GB DocLayNet or 40GB PubLayNet) would destabilize the host system.

IntelliGrade establishes the following safety rules in `scripts/download_datasets.py`:
1. **Pre-flight Free Space Verification:** No download may begin unless free disk space exceeds `Required Space * 2.5` AND remaining free space after download remains > 10.0 GB.
2. **Dataset Manifests & Remote Schemas:** All 10 candidate datasets are catalogued via SHA-256 manifests, schema definitions, and licensing metadata in `config/datasets.yaml`.
3. **Synthetic / Sample Micro-Datasets:** Local evaluation runs on targeted, lightweight synthetic test fixtures (50–200 KB each) rather than massive multi-GB archives.
4. **Single Cached Transformer:** Worker instances share memory-mapped transformer weights rather than duplicating models across subprocesses.

---

## 4. Concurrency & Worker Tuning

Given 12 logical cores and constrained available RAM:
- **FastAPI Uvicorn Workers:** 1 main asynchronous event loop process.
- **Celery Worker Concurrency:** Windows solo worker (`--pool=solo`) or 2 worker processes with dedicated queues:
  - `ocr`: 1 worker (serialized to avoid EasyOCR PyTorch memory spikes).
  - `evaluation`: 1 worker (batches embedding inferences).
  - `plagiarism`: 1 worker (lightweight vectorized matrix operations).
  - `reports` & `default`: Shared lightweight background worker.

---

## 5. Model Benchmarking Gates

Any model candidate considered for promotion to production must satisfy:
1. **Inference Latency:** < 2.5 seconds per script page on CPU.
2. **Peak Memory Consumption:** < 600 MB resident memory increase during batch inference.
3. **Grading Accuracy:** Mean Absolute Error (MAE) <= 1.25 marks compared to calibrated teacher standards.
4. **OCR Word Error Rate (WER):** <= 0.15 on standard legible handwriting samples.
