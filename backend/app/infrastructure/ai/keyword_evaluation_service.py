"""
infrastructure/ai/keyword_evaluation_service.py — Keyword Coverage Engine
"""

from __future__ import annotations

import re
import string


class KeywordEvaluationService:
    """
    Evaluates student answer coverage against expected key concepts/keywords.
    """

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for keyword matching: lowercase, remove punctuation except spaces.
        """
        text = text.lower()
        # Remove punctuation, but keep spaces
        translator = str.maketrans("", "", string.punctuation)
        return text.translate(translator)

    def evaluate_keywords(self, student_answer: str, expected_keywords: list[str]) -> dict:
        """
        Compares student answer against expected keywords list.

        Returns:
            dict containing:
                "keyword_score": float (0.0 to 1.0)
                "keyword_coverage_percentage": float (0.0 to 100.0)
                "matched_keywords": list[str]
                "missing_keywords": list[str]
        """
        if not expected_keywords:
            return {
                "keyword_score": 1.0,
                "keyword_coverage_percentage": 100.0,
                "matched_keywords": [],
                "missing_keywords": []
            }

        normalized_student = self._normalize_text(student_answer)
        
        matched = []
        missing = []

        for kw in expected_keywords:
            clean_kw = self._normalize_text(kw).strip()
            if not clean_kw:
                continue
            
            # Use regex pattern to match keyword as word boundary or exact substring
            # We want to match root words or phrases, e.g., "artificial intelligence"
            pattern = re.compile(rf"\b{re.escape(clean_kw)}\b")
            
            if pattern.search(normalized_student) or clean_kw in normalized_student:
                matched.append(kw)
            else:
                missing.append(kw)

        total_kws = len(expected_keywords)
        coverage_fraction = len(matched) / total_kws if total_kws > 0 else 1.0
        
        return {
            "keyword_score": coverage_fraction,
            "keyword_coverage_percentage": coverage_fraction * 100.0,
            "matched_keywords": matched,
            "missing_keywords": missing
        }
