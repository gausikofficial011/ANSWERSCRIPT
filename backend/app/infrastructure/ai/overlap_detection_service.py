"""
infrastructure/ai/overlap_detection_service.py — Overlap Detection Service
"""

from __future__ import annotations
import re


class OverlapDetectionService:
    """
    Computes exact phrase overlaps and token set intersections.
    """

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute similarity score based on exact overlap of tokens and word n-grams.
        """
        if not text1.strip() or not text2.strip():
            return 0.0

        t1 = text1.strip().lower()
        t2 = text2.strip().lower()
        if t1 == t2:
            return 1.0

        # Clean punctuation and tokenize
        tokens1 = re.findall(r"\b\w+\b", t1)
        tokens2 = re.findall(r"\b\w+\b", t2)

        if not tokens1 or not tokens2:
            return 0.0

        # 1. Token Set Intersection (Jaccard similarity)
        set1 = set(tokens1)
        set2 = set(tokens2)
        jaccard = len(set1 & set2) / len(set1 | set2)

        # 2. Word N-gram Overlap (n=3)
        def get_word_ngrams(tokens: list[str], n: int = 3) -> set[tuple[str, ...]]:
            if len(tokens) < n:
                return set([tuple(tokens)])
            return set(tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1))

        ngrams1 = get_word_ngrams(tokens1, 3)
        ngrams2 = get_word_ngrams(tokens2, 3)

        intersection = ngrams1 & ngrams2
        union = ngrams1 | ngrams2
        
        ngram_similarity = len(intersection) / len(union) if union else 0.0

        # Weighted combination: 40% Jaccard, 60% n-gram overlap
        score = 0.4 * jaccard + 0.6 * ngram_similarity
        return float(min(1.0, max(0.0, score)))
