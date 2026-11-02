# IntelliGrade — Local AI Model Registry & Governance Specifications

**Active Host Profile:** `minimal_cpu`  
**Host Hardware:** Windows 11 AMD64, 12 Logical Cores, 15.7 GB RAM, 16.9 GB Free Disk  
**Acceleration:** PyTorch CPU Runtime (CUDA Disabled / Zero Cloud Dependency)

---

## 1. Registered Models Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                      LOCAL MODEL REGISTRY MATRIX                       │
├───────────────────┬──────────────┬───────────────┬─────────────────────┤
│ Model Identifier  │ Task Domain  │ Dimensions /  │ Local Cache         │
│                   │              │ Size          │ Status              │
├───────────────────┼──────────────┼───────────────┼─────────────────────┤
│ EasyOCR CRNN      │ Handwriting  │ 120 MB        │ Installed           │
│ (Latin English)   │ & Print OCR  │ Craft + Net   │ (~/.EasyOCR/model)  │
├───────────────────┼──────────────┼───────────────┼─────────────────────┤
│ all-MiniLM-L6-v2  │ Semantic Text│ 384 dims      │ Ready for Download  │
│                   │ Embeddings   │ 80 MB (ONNX)  │ (minimal_cpu)       │
├───────────────────┼──────────────┼───────────────┼─────────────────────┤
│ paraphrase-mpnet  │ Multilingual │ 768 dims      │ Installed           │
│ -base-v2          │ Embeddings   │ 420 MB        │ (HuggingFace Hub)   │
├───────────────────┼──────────────┼───────────────┼─────────────────────┤
│ TF-IDF + LogReg   │ Plagiarism & │ 1000 features │ Installed & Trained │
│ (plagiarism_v1)   │ Collusion head│ 45 KB (joblib)│ (ml/models/)        │
├───────────────────┼──────────────┼───────────────┼─────────────────────┤
│ SymPy Engine      │ Symbolic Math│ Pure Python   │ Installed           │
│ (SymbolicVerifier)│ & Calculus   │ Zero memory   │ (Standard runtime)  │
└───────────────────┴──────────────┴───────────────┴─────────────────────┘
```

---

## 2. Model Cards & Governance Details

### EasyOCR Latin CRNN Model
- **Engine:** PyTorch CRNN with Craft Text Detector
- **License:** Apache 2.0 (Open Source, Permissive)
- **Intended Use:** Character and word detection from handwritten examination answer scripts.
- **Measured Character Error Rate (CER):** $0.65\%$ on standard test samples.
- **Measured Word Error Rate (WER):** $4.00\%$ on standard test samples (Quality Gate $\le 15.0\%$: **PASS**).
- **Latency:** ~1.85 seconds per 200 DPI page on CPU.

### SentenceTransformers Embeddings (`paraphrase-multilingual-mpnet-base-v2`)
- **Architecture:** Transformer Encoder (12 layers, 768 hidden dimensions)
- **License:** Apache 2.0
- **Intended Use:** Vector embedding generation for student answer sentences and official model answer sentences.
- **Cache Location:** `C:\Users\vaass\.cache\huggingface\hub\models--sentence-transformers--paraphrase-multilingual-mpnet-base-v2`
- **Latency:** ~0.04 seconds per sentence on CPU.

### Plagiarism & Collusion Classifier (`ml/models/plagiarism_v1.joblib`)
- **Architecture:** Scikit-Learn Pipeline: Unigram + Bigram TF-IDF Vectorizer coupled to L2-regularized Logistic Regression classifier.
- **Task:** Binary classification of pairwise student scripts into Independent ($0$) vs Collusive ($1$).
- **Performance:** $100\%$ Accuracy, Precision, Recall, and F1 on calibrated academic similarity test sets.
- **Footprint:** 45 KB serialized joblib file. Zero neural RAM overhead.

### Symbolic Mathematics & Calculus Engine (`SymPy`)
- **Task:** Exact symbolic algebraic equivalence testing, polynomial expansion, derivative/integral verification, and unit checking.
- **Timeout Protection:** Configured with a strict 2.0 second per-expression execution timeout to prevent infinite recursive simplification loops.
