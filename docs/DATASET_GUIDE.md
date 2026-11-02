# IntelliGrade — Academic Dataset Catalogue & Ingestion Guide

**Storage Policy:** Strict Storage Budget & Download Safeguard Enforcement  
**Host Free Space Threshold:** &ge; 10.0 GB Minimum Free Disk Required Before Any Download

---

## 1. Candidate Academic Datasets Directory

IntelliGrade indexes ten major academic document and handwriting benchmarks in `config/datasets.yaml`:

```
┌────┬─────────────────────────────┬───────────┬──────────────┬─────────────────────────────┐
│ #  │ Dataset Name                │ Size      │ License      │ Ingestion Status            │
├────┼─────────────────────────────┼───────────┼──────────────┼─────────────────────────────┤
│ 1  │ Gopika13 Answer Scripts     │ 48.5 MB   │ CC-BY-4.0    │ Active Sample Fixture       │
│ 2  │ IAM Handwriting Database    │ 1,150 MB  │ Academic     │ Manifest Only (Protected)   │
│ 3  │ DocLayNet Document Layouts  │ 28,400 MB │ CDLA-1.0     │ Manifest Only (Protected)   │
│ 4  │ FUNSD Form Understanding    │ 16.2 MB   │ MIT          │ Manifest Only               │
│ 5  │ CROHME Math Expressions     │ 85.0 MB   │ Academic     │ Manifest Only               │
│ 6  │ PubLayNet Scientific Papers │ 42,000 MB │ CDLA-1.0     │ Manifest Only (Protected)   │
│ 7  │ RVL-CDIP Categories         │ 37,500 MB │ Research     │ Manifest Only (Protected)   │
│ 8  │ SROIE Structured Receipts   │ 120.0 MB  │ Competition  │ Manifest Only               │
│ 9  │ DocBank Token Layouts       │ 55,000 MB │ Academic     │ Manifest Only (Protected)   │
│ 10 │ STSb Semantic Benchmark     │ 1.4 MB    │ CC-BY-SA 4.0 │ Active Sample Fixture       │
└────┴─────────────────────────────┴───────────┴──────────────┴─────────────────────────────┘
```

---

## 2. Download Safety Safeguards & Guardrails

To prevent disk exhaustion on host systems with bounded free space (e.g., 16.9 GB free on host):

1. **Pre-Flight Disk Quota Check:** `scripts/download_datasets.py` computes available drive capacity via `shutil.disk_usage()`. If free space is below `10.0 GB`, live downloads are hard-blocked.
2. **Threshold Capping:** Any single dataset archive exceeding `500 MB` is prevented from downloading and preserved as an SHA-256 manifest.
3. **Local Micro-Fixtures:** Regression and accuracy tests operate on verified, zero-risk JSON sample fixtures stored in:
   - `ml/datasets/processed/answer_scripts_sample.json` (OCR CER/WER)
   - `ml/datasets/processed/stsb_sample.json` (Semantic similarity correlation)
   - `ml/datasets/processed/intelligrade_golden_set.json` (Teacher-calibrated ground truth marks)

---

## 3. Command Usage

Inspect dataset manifests in dry-run mode:
```powershell
python scripts/download_datasets.py
```

Inspect a specific dataset:
```powershell
python scripts/download_datasets.py --id gopika13-answer-scripts
```
