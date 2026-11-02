# MCA Final Project Report - AI Answer Evaluation System

This document constitutes the formal MCA project submission document.

---

## 1. Abstract
The AI Answer Evaluation System is a web-based application designed to automate the grading of handwritten student answer sheets. Combining high-resolution PDF extraction, OCR, and advanced NLP semantic analysis, the system evaluates student responses against model answer sheets using criteria-based rubrics. It provides a human-in-the-loop interface for teachers to override grades, maintaining transparency and academic integrity.

## 2. Problem Statement
Manual grading of handwritten answer sheets is time-consuming, prone to subjective bias, and susceptible to evaluation inconsistencies across large classes.

## 3. Existing System
The existing system is manual. Physical papers are collected, sorted, graded by multiple teachers, and marks entered manually into spreadsheets. This process suffers from slow turnaround times and lacks automated validation or plagiarism checks.

## 4. Proposed System
The proposed system automates the grading workflow using AI. Handwritten papers are scanned and uploaded as PDFs. An OCR engine extracts the text, a RegEx engine maps segments to exam questions, and SentenceTransformers compare responses to model answers. The system calculates grades and scans for plagiarism automatically.

## 5. Objectives
* Build a reliable E2E pipeline for digitizing and evaluating handwritten scripts.
* Eliminate grading bias and speed up result generation.
* Implement human-in-the-loop review screens.

## 6. Technologies Used
* **Backend**: FastAPI (Python), PostgreSQL, Redis, Celery.
* **Frontend**: React, Vite, CSS, Lucide Icons.
* **AI Libraries**: EasyOCR, PyTorch, SentenceTransformers (all-MiniLM-L6-v2), NLTK.

## 7. AI Techniques Used
* **Computer Vision**: Text bounding box localization.
* **Natural Language Processing**: Semantic text encoding, Porter Stemming, cosine similarity scoring.

## 8. Architecture Diagram
Detailed high-level block diagram outlining UI, Backend, DB, and background Celery layers (see `SYSTEM_ARCHITECTURE.md`).

## 9. Database Design
Entity-relationship layout containing tables for users, answer sheets, evaluations, and rubrics (see `DATABASE_DOCUMENTATION.md`).

## 10. Module Description
* **Authentication**: Handles stateless JWT login and roles.
* **Upload**: Handles validation, virus scans, and local storage.
* **OCR**: Converts PDFs and extracts text.
* **Scoring Engine**: Evaluates answers using semantic similarity, keywords, and criteria rubrics.
* **Plagiarism Scanner**: Performs pairwise similarity checks.
* **Reporting**: Exports performance sheets in PDF format.

## 11. Algorithms
* Cosine Similarity for semantic matching.
* porter Stemmer for keyword matches.
* RegEx text boundaries mapping.

## 12. OCR Workflow
Converts PDF pages to PNGs, processes them via EasyOCR, and returns layout text.

## 13. AI Evaluation Workflow
Compares segmented text with model answers, computes sub-scores, and aggregates them.

## 14. Plagiarism Detection
Pairwise comparisons between student text submissions.

## 15. Results
E2E pipeline processes a 13-page answer sheet in 96.73 seconds, generating grading lists and annotations.

## 16. Advantages
* Reduces grading turn-around time.
* Standardizes criteria-based grading.
* Identifies copying automatically.

## 17. Limitations
* Dependent on handwriting legibility.
* Requires server resources for PyTorch model inference.

## 18. Future Scope
* Integration of LLMs (like Gemini API) for detailed text feedback.
* GPU acceleration to speed up OCR.

## 19. Conclusion
The AI Answer Evaluation System successfully demonstrates the feasibility of combining computer vision and natural language processing to create a transparent, automated grading tool for academic institutions.
