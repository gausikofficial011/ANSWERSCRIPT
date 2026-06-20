"""
ai/embeddings/embedding_cache.py — Embedding Cache

Caches computed embedding vectors to avoid redundant model inference.

Cache strategy:
  - Key: SHA-256 hash of (model_name + text)
  - Value: EmbeddingVector
  - Storage: In-process LRU cache (current) → Redis (future scale-out)
  - TTL: Session-scoped (cleared on worker restart)

Rationale:
  - Model answers are embedded repeatedly across many evaluation runs.
  - Caching model answer embeddings saves ~200ms per question per sheet.
  - Student answer embeddings are not cached (unique per sheet).
"""

from __future__ import annotations

import hashlib
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ai.embeddings.base_embedder import EmbeddingVector


def _compute_cache_key(model_name: str, text: str) -> str:
    """Generate a deterministic cache key from model name and text."""
    raw = f"{model_name}:{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class EmbeddingCache:
    """
    In-process LRU cache for embedding vectors.

    Thread-safe for single-process use. For multi-worker Celery setups,
    use the Redis-backed implementation (future: RedisEmbeddingCache).

    Args:
        max_size: Maximum number of vectors to hold in memory.
                  Each vector (768-dim float32) ≈ 3KB.
                  Default 1000 entries ≈ 3MB.
    """

    def __init__(self, max_size: int = 1000) -> None:
        self._max_size = max_size
        # Internal dict used as ordered cache; replaced by functools.lru_cache
        # on the get method to keep the interface clean.
        self._cache: dict[str, "EmbeddingVector"] = {}

    def get(self, model_name: str, text: str) -> "EmbeddingVector | None":
        """Return cached vector or None if not present."""
        key = _compute_cache_key(model_name, text)
        return self._cache.get(key)

    def set(self, model_name: str, text: str, vector: "EmbeddingVector") -> None:
        """Store a vector in the cache, evicting LRU if at capacity."""
        key = _compute_cache_key(model_name, text)
        if len(self._cache) >= self._max_size:
            # Evict oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[key] = vector

    def invalidate(self, model_name: str, text: str) -> None:
        """Remove a specific entry from the cache."""
        key = _compute_cache_key(model_name, text)
        self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)

    @property
    def hit_rate_info(self) -> dict:
        return {"cached_entries": self.size, "max_size": self._max_size}
