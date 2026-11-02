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
        Compares student answer against expected keywords list with synonym expansion and lemmatization.

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

        from app.infrastructure.ai.text_normalization_service import TextNormalizationService
        from app.infrastructure.ai.synonym_dictionary_service import SynonymDictionaryService

        normalizer = TextNormalizationService()
        synonym_service = SynonymDictionaryService()

        # 1. Normalize and lemmatize student's answer
        student_tokens = normalizer.normalize_text(student_answer)
        normalized_student_str = " ".join(student_tokens)

        matched = []
        missing = []

        for kw in expected_keywords:
            # 2. Expand keyword synonyms
            synonyms = synonym_service.expand_keywords([kw])
            
            # 3. Check if any synonym matches the student's answer
            is_matched = False
            for syn in synonyms:
                # Normalize and lemmatize the synonym phrase
                syn_tokens = normalizer.normalize_text(syn)
                normalized_syn_str = " ".join(syn_tokens)
                
                if not normalized_syn_str:
                    continue

                # Check if it matches exactly as a sub-phrase
                pattern = re.compile(rf"\b{re.escape(normalized_syn_str)}\b")
                if pattern.search(normalized_student_str) or normalized_syn_str in normalized_student_str:
                    is_matched = True
                    break

            if is_matched:
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
