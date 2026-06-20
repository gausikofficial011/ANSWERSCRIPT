"""
infrastructure/ai/semantic_similarity_service.py — Semantic Similarity Scorer
"""

from __future__ import annotations

from app.ai.embeddings.sentence_transformer_embedder import SentenceTransformerEmbedder
from app.ai.similarity.cosine_similarity import cosine_similarity


class SemanticSimilarityService:
    """
    Computes semantic similarity score between two texts using multilingual embeddings.
    """

    def __init__(self, embedder: SentenceTransformerEmbedder | None = None) -> None:
        self.embedder = embedder or SentenceTransformerEmbedder()

    def compute_similarity(self, student_answer: str, model_answer: str) -> float:
        """
        Compute similarity score clamped to [0.0, 1.0].
        """
        if not student_answer.strip() or not model_answer.strip():
            return 0.0

        student_embedding = self.embedder.encode(student_answer)
        model_embedding = self.embedder.encode(model_answer)

        try:
            return cosine_similarity(student_embedding, model_embedding)
        except Exception:
            return 0.0
