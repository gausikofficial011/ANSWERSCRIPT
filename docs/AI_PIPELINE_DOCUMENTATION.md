# AI Evaluation Pipeline Documentation

This document explains the technical algorithms, models, and execution flow of the AI Answer Evaluation system.

---

## 1. Step-by-Step AI Core Architecture

```
[Answer Sheet PDF]
       |
       v  (pdf2image + Poppler)
[Page Images (PNG/JPG)]
       |
       v  (EasyOCR Text Extraction)
[OCR Raw Transcripts]
       |
       v  (RegEx Pattern Headers Mapping)
[Segmented Answer Blocks]
       |
       +-----------------------+----------------------+
       |                       |                      |
       v                       v                      v
[Semantic Cosine Sim]    [Keyword Stemming]     [Criteria Rubric matching]
 SentenceTransformers     Synonym Mapping        Weights calculation
       |                       |                      |
       +-----------------------+----------------------+
                               |
                               v
                     [Aggregated Scoring]
                     (Weighted Average)
                               |
                               v
                  [Confidence Metric Calc]
                               |
                               v
                     [Teacher Review Hook]
```

---

## 2. Technical Component Deep-Dive

### OCR Text Extraction Engine
* **Technology**: `EasyOCR` + `PyTorch` + `pdf2image`.
* **Flow**: PDFs are converted to high-contrast images. EasyOCR performs localization (finding word bounding boxes) and text recognition, returning raw text strings and layout confidence values.

### RegEx Question Mapping & Segmentation
* **Algorithm**: Scans raw OCR texts for patterns indicating question starts (e.g., `(?i)(q|question|ans|answer)\s*(\d+)`).
* **Segmentation**: Text following a detected boundary is mapped to that question ID until the next header is matched.

### NLP Grading Algorithms
1. **Semantic Similarity**:
   * Uses Sentence Transformers `all-MiniLM-L6-v2`.
   * Encodes the segmented student response and the model answer into dense 384-dimensional vectors.
   * Calculates cosine similarity:
     $$	ext{Similarity} = rac{A \cdot B}{\|A\| \|B\|}$$
2. **Keyword Stemming**:
   * Stems extracted words using Porter Stemming.
   * Compares them with expected keywords and synonyms to compute the ratio of matched concepts.
3. **Criteria Rubric Blending**:
   * Maps criteria keywords to student text segments.
   * Multiplies the matching ratio by the criteria weight to produce the rubric score.

### Aggregate Scoring
Scores are aggregated based on configured exam weights (e.g. 20% Semantic, 30% Keywords, 50% Rubrics).

### Confidence Score Calculation
$$	ext{Confidence} = 	ext{OCR Avg Confidence} 	imes (1.0 - |	ext{AI Score} - 	ext{Semantic Score}|)$$
If confidence falls below a preset threshold (default 60%), the evaluation is flagged for manual teacher review.
