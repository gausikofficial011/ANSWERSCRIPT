# IntelliGrade — Quality Assurance & Testing Suite

**Automated Test Framework:** `pytest` (Backend) + `tsc` & `vite build` (Frontend)  
**Recorded Pass Rate:** 100% of Unit and Infrastructure Tests Passing

---

## 1. Test Suite Summary

```
┌─────────────────────────────────┬───────────┬──────────────┬────────┐
│ Test Suite                      │ Tests Run │ Passed Count │ Status │
├─────────────────────────────────┼───────────┼──────────────┼────────┤
│ Backend Unit Tests              │ 89        │ 89           │ PASS   │
│ Backend Infrastructure Tests    │ 13        │ 13           │ PASS   │
│ Model Benchmark Suite           │ 3 Gates   │ 3            │ PASS   │
│ Frontend TypeScript Build (tsc) │ 1866 mods │ 1866         │ PASS   │
│ YAML Configuration Validator    │ 16 files  │ 16           │ PASS   │
└─────────────────────────────────┴───────────┴──────────────┴────────┘
```

---

## 2. Test Execution Commands

### Run Backend Unit Tests:
```powershell
cd C:\ANSWERSCRIPT\backend
.\.venv\Scripts\python.exe -m pytest tests/unit -v
```

### Run YAML Configuration Validation:
```powershell
cd C:\ANSWERSCRIPT\backend
.\.venv\Scripts\python.exe -m app.core.config_validator
```

### Run Model Regression Benchmark:
```powershell
cd C:\ANSWERSCRIPT\backend
.\.venv\Scripts\python.exe scripts/benchmark_models.py
```

### Run Lightweight Plagiarism Classifier Training:
```powershell
cd C:\ANSWERSCRIPT\backend
.\.venv\Scripts\python.exe scripts/train_small_models.py
```

### Run Frontend Production Build:
```powershell
cd C:\ANSWERSCRIPT\frontend
npm run build
```

---

## 3. Verified Benchmark Quality Gates

- **OCR Character Error Rate (CER):** $0.65\%$ (Standard legible handwriting)
- **OCR Word Error Rate (WER):** $4.00\%$ (Quality Gate: $\le 15.0\% \implies$ **PASS**)
- **STSb Semantic Similarity Correlation:** MAE $0.5074$
- **Grading Mean Absolute Error (MAE):** $0.20$ marks on golden calibrated ground truth (Quality Gate: $\le 1.25$ marks $\implies$ **PASS**)
