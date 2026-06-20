"""
infrastructure/ai/semantic_plagiarism_service.py — Semantic Plagiarism Service
"""

from __future__ import annotations
from typing import Dict
import uuid

from app.ai.embeddings.sentence_transformer_embedder import SentenceTransformerEmbedder
from app.ai.similarity.cosine_similarity import cosine_similarity


class SemanticPlagiarismService:
    """
    Computes semantic similarity between answers.
    """

    def __init__(self, embedder: SentenceTransformerEmbedder | None = None) -> None:
        self.embedder = embedder or SentenceTransformerEmbedder()

    def compute_similarity(
        self,
        text1: str,
        text2: str,
        embedding1: list[float] | None = None,
        embedding2: list[float] | None = None
    ) -> float:
        """
        Compute similarity score between two texts.
        If pre-computed embeddings are provided, use them to avoid re-encoding.
        """
        if not text1.strip() or not text2.strip():
            return 0.0

        emb1 = embedding1 if embedding1 is not None else self.embedder.encode(text1)
        emb2 = embedding2 if embedding2 is not None else self.embedder.encode(text2)

        try:
            return float(cosine_similarity(emb1, emb2))
        except Exception:
            return 0.0

    def get_embedding(self, text: str) -> list[float]:
        """
        Generates and returns the embedding vector for a given text.
        """
        return self.embedder.encode(text)
