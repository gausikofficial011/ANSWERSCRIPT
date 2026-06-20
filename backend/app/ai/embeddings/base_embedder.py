"""
ai/embeddings/base_embedder.py — Abstract Text Embedder Interface

Defines the protocol all embedding implementations must satisfy.
This abstraction allows swapping between:
  - SentenceTransformers (current implementation)
  - OpenAI text-embedding-ada-002 (future)
  - Google Vertex AI embeddings (future)
  - Local GGUF quantized models (future edge deployment)

Design:
  - Returns numpy arrays or Python lists (framework-agnostic)
  - encode_batch() is the performance-critical path
  - encode() is a convenience wrapper around encode_batch()
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Union

# Type alias: embedding vector is a list of floats
EmbeddingVector = list[float]


class BaseTextEmbedder(ABC):
    """
    Abstract interface for text-to-vector embedding models.

    All implementations must be thread-safe for use within Celery workers.
    Model loading should happen in __init__ and be cached (lazy or eager).
    """

    @abstractmethod
    def encode(self, text: str) -> EmbeddingVector:
        """
        Encode a single text string into an embedding vector.

        Args:
            text: The input text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        ...

    @abstractmethod
    def encode_batch(self, texts: list[str]) -> list[EmbeddingVector]:
        """
        Encode multiple texts in a single batched forward pass.

        Implementations should use this for all bulk operations
        (plagiarism detection, batch evaluation) as it is significantly
        faster than calling encode() in a loop.

        Args:
            texts: List of input texts.

        Returns:
            List of embedding vectors in the same order as input texts.
        """
        ...

    @abstractmethod
    def vector_dimension(self) -> int:
        """Return the output vector dimensionality for this model."""
        ...

    @abstractmethod
    def model_name(self) -> str:
        """Return a human-readable model identifier for logging and versioning."""
        ...

    @abstractmethod
    def supported_languages(self) -> list[str]:
        """
        Return list of ISO 639-1 language codes supported by this embedder.
        Used to validate language compatibility before encoding.
        """
        ...
