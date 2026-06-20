"""
ai/embeddings/sentence_transformer_embedder.py — SentenceTransformer Embedder Implementation
"""

from __future__ import annotations

import logging
from typing import ClassVar
from sentence_transformers import SentenceTransformer

from app.ai.embeddings.base_embedder import BaseTextEmbedder, EmbeddingVector
from app.ai.embeddings.embedding_cache import EmbeddingCache
from app.config import get_settings

logger = logging.getLogger(__name__)


class SentenceTransformerEmbedder(BaseTextEmbedder):
    """
    Concrete embedding extractor using local sentence-transformers.
    Thread-safe and utilizes EmbeddingCache for caching.
    """

    _model_instance: ClassVar[SentenceTransformer | None] = None
    _cache: ClassVar[EmbeddingCache] = EmbeddingCache()

    def __init__(self) -> None:
        self.settings = get_settings()
        self._model_name = self.settings.sentence_transformer_model
        
        # Load model lazily as a singleton across all workers/instances
        if SentenceTransformerEmbedder._model_instance is None:
            logger.info(f"Loading SentenceTransformer model: {self._model_name}...")
            # Weasyprint/PyTorch CPU thread tuning can be added if needed, but defaults are fine
            SentenceTransformerEmbedder._model_instance = SentenceTransformer(self._model_name)
            logger.info("SentenceTransformer model loaded successfully.")

    @property
    def model(self) -> SentenceTransformer:
        if self._model_instance is None:
            # Fallback if somehow not initialized
            self._model_instance = SentenceTransformer(self._model_name)
        return self._model_instance

    def encode(self, text: str) -> EmbeddingVector:
        """
        Encode a single string, using the LRU cache if hit.
        """
        if not text.strip():
            # Return empty/zero vector or handle empty gracefully
            dim = self.vector_dimension()
            return [0.0] * dim

        cached = self._cache.get(self._model_name, text)
        if cached is not None:
            return cached

        # Inference
        vector = self.model.encode(text, convert_to_numpy=True).tolist()
        self._cache.set(self._model_name, text, vector)
        return vector

    def encode_batch(self, texts: list[str]) -> list[EmbeddingVector]:
        """
        Encode a list of strings efficiently, leveraging cache for hits.
        """
        results: list[EmbeddingVector | None] = [None] * len(texts)
        missing_indices: list[int] = []
        missing_texts: list[str] = []

        # Check cache first
        for i, text in enumerate(texts):
            if not text.strip():
                results[i] = [0.0] * self.vector_dimension()
                continue
            cached = self._cache.get(self._model_name, text)
            if cached is not None:
                results[i] = cached
            else:
                missing_indices.append(i)
                missing_texts.append(text)

        # Batch encode missing ones
        if missing_texts:
            encoded_vectors = self.model.encode(missing_texts, convert_to_numpy=True)
            for idx, vec in zip(missing_indices, encoded_vectors):
                vector_list = vec.tolist()
                results[idx] = vector_list
                # Set in cache
                self._cache.set(self._model_name, texts[idx], vector_list)

        # All results should be non-None
        return [r for r in results if r is not None]

    def vector_dimension(self) -> int:
        """
        Return the dimension of the embedding vectors.
        mpnet usually outputs 768 dimensions.
        """
        if "mpnet" in self._model_name:
            return 768
        # Fallback query model directly
        return self.model.get_sentence_embedding_dimension() or 768

    def model_name(self) -> str:
        return self._model_name

    def supported_languages(self) -> list[str]:
        """
        ISO 639-1 language codes. paraphrase-multilingual-mpnet-base-v2 supports
        over 50 languages, including Hindi ('hi'), Tamil ('ta'), English ('en').
        """
        return ["en", "hi", "ta", "mr", "te", "ur"]
