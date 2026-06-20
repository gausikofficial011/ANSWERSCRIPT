"""
ai/similarity/similarity_matrix.py — Pairwise Similarity Matrix

Computes an N×N similarity matrix for all answer sheets in an exam.
Used exclusively by the plagiarism detection pipeline.

Complexity: O(N²) — acceptable for exam scale (N < 500 students per exam).
For N > 500, use approximate nearest neighbor (future: FAISS).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.ai.similarity.cosine_similarity import cosine_similarity

if TYPE_CHECKING:
    from app.ai.embeddings.base_embedder import EmbeddingVector


@dataclass(frozen=True)
class SimilarityPair:
    """A pair of answer sheet IDs and their similarity score."""
    source_id: str
    target_id: str
    similarity: float

    @property
    def as_percentage(self) -> float:
        return round(self.similarity * 100, 2)


class SimilarityMatrix:
    """
    Pairwise cosine similarity matrix for plagiarism detection.

    Usage:
        matrix = SimilarityMatrix(answer_vectors)
        pairs = matrix.pairs_above_threshold(threshold=0.85)
    """

    def __init__(
        self,
        answer_vectors: dict[str, "EmbeddingVector"],
    ) -> None:
        """
        Args:
            answer_vectors: Mapping of {answer_sheet_id: embedding_vector}.
                            All vectors must have the same dimension.
        """
        self._ids = list(answer_vectors.keys())
        self._vectors = list(answer_vectors.values())
        self._n = len(self._ids)
        # Precomputed upper-triangle matrix (N×N)
        self._matrix: list[list[float]] | None = None

    def compute(self) -> "SimilarityMatrix":
        """
        Compute all pairwise similarities. Call this before querying.
        Returns self for chaining.
        """
        n = self._n
        self._matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            self._matrix[i][i] = 1.0   # Self-similarity = 1.0
            for j in range(i + 1, n):
                sim = cosine_similarity(self._vectors[i], self._vectors[j])
                self._matrix[i][j] = sim
                self._matrix[j][i] = sim   # Symmetric

        return self

    def get(self, source_id: str, target_id: str) -> float:
        """Return similarity score between two specific answer sheets."""
        if self._matrix is None:
            raise RuntimeError("Call compute() before querying the matrix.")
        i = self._ids.index(source_id)
        j = self._ids.index(target_id)
        return self._matrix[i][j]

    def pairs_above_threshold(self, threshold: float) -> list[SimilarityPair]:
        """
        Return all unique pairs with similarity >= threshold.
        Only upper triangle is returned (avoids duplicates).
        """
        if self._matrix is None:
            raise RuntimeError("Call compute() before querying the matrix.")

        pairs: list[SimilarityPair] = []
        for i in range(self._n):
            for j in range(i + 1, self._n):
                sim = self._matrix[i][j]
                if sim >= threshold:
                    pairs.append(SimilarityPair(
                        source_id=self._ids[i],
                        target_id=self._ids[j],
                        similarity=sim,
                    ))
        # Sort by similarity descending for report ordering
        return sorted(pairs, key=lambda p: p.similarity, reverse=True)
