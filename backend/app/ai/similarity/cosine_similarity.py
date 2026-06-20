"""
ai/similarity/cosine_similarity.py — Cosine Similarity Calculator

Pure mathematical function module with no external AI dependencies.
Used by both the evaluation pipeline and the plagiarism detector.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ai.embeddings.base_embedder import EmbeddingVector


def cosine_similarity(vec_a: "EmbeddingVector", vec_b: "EmbeddingVector") -> float:
    """
    Compute cosine similarity between two embedding vectors.

    Returns a float in [0.0, 1.0] where:
      1.0 = identical direction (semantically identical)
      0.0 = orthogonal (completely unrelated)
     -1.0 = opposite direction (not possible with normalized sentence embeddings)

    Args:
        vec_a: First embedding vector.
        vec_b: Second embedding vector.

    Returns:
        Cosine similarity score clamped to [0.0, 1.0].

    Raises:
        ValueError: If vectors are empty or have different dimensions.
    """
    if not vec_a or not vec_b:
        raise ValueError("Embedding vectors must not be empty.")
    if len(vec_a) != len(vec_b):
        raise ValueError(
            f"Vector dimension mismatch: {len(vec_a)} vs {len(vec_b)}."
        )

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    raw_similarity = dot_product / (mag_a * mag_b)
    # Clamp to [0.0, 1.0] — negative values are not meaningful for sentence embeddings
    return max(0.0, min(1.0, raw_similarity))


def batch_cosine_similarity(
    query_vec: "EmbeddingVector",
    candidate_vecs: list["EmbeddingVector"],
) -> list[float]:
    """
    Compute cosine similarity between one query vector and many candidates.

    More efficient than calling cosine_similarity() in a loop because
    the query vector's magnitude is computed only once.

    Args:
        query_vec:       The query embedding vector.
        candidate_vecs:  List of candidate embedding vectors.

    Returns:
        List of similarity scores in [0.0, 1.0], same order as candidate_vecs.
    """
    if not query_vec:
        raise ValueError("Query vector must not be empty.")

    mag_query = math.sqrt(sum(a * a for a in query_vec))
    if mag_query == 0.0:
        return [0.0] * len(candidate_vecs)

    results: list[float] = []
    for vec in candidate_vecs:
        dot = sum(a * b for a, b in zip(query_vec, vec))
        mag = math.sqrt(sum(b * b for b in vec))
        if mag == 0.0:
            results.append(0.0)
        else:
            raw = dot / (mag_query * mag)
            results.append(max(0.0, min(1.0, raw)))

    return results
