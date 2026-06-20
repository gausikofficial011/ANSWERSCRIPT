"""
infrastructure/ai/lexical_similarity_service.py — Lexical Similarity Service
"""

from __future__ import annotations
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LexicalSimilarityService:
    """
    Computes lexical similarity using TF-IDF + Cosine Similarity.
    """

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute similarity score between two texts.
        """
        if not text1.strip() or not text2.strip():
            return 0.0

        # Normalization and simple edge cases
        t1 = text1.strip().lower()
        t2 = text2.strip().lower()
        if t1 == t2:
            return 1.0

        try:
            vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity[0][0])
        except Exception:
            return 0.0
