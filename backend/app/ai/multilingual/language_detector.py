"""
ai/multilingual/language_detector.py — Language Detection Interface

Wraps a language detection library behind an abstract interface.
Current implementation: langdetect (offline, fast).
Future: fasttext with lid.176.bin model (more accurate).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DetectedLanguage:
    """
    Result of language detection on a text sample.

    Attributes:
        code:       ISO 639-1 language code (e.g., "en", "ta").
        confidence: Detection confidence in [0.0, 1.0].
        is_reliable: True if confidence >= 0.85 (system threshold).
    """
    code: str
    confidence: float

    RELIABLE_THRESHOLD: float = 0.85

    @property
    def is_reliable(self) -> bool:
        return self.confidence >= self.RELIABLE_THRESHOLD

    def __str__(self) -> str:
        return f"{self.code} ({self.confidence:.2%})"


class BaseLanguageDetector(ABC):
    """
    Abstract interface for text language detection.

    Implementations must be thread-safe for Celery worker use.
    """

    @abstractmethod
    def detect(self, text: str) -> DetectedLanguage:
        """
        Detect the primary language of the given text.

        Args:
            text: The text to analyze (minimum 20 characters recommended).

        Returns:
            DetectedLanguage with ISO code and confidence.
        """
        ...

    @abstractmethod
    def detect_batch(self, texts: list[str]) -> list[DetectedLanguage]:
        """
        Detect language for multiple texts in one call.
        Implementations should optimize for batch throughput.
        """
        ...

    @abstractmethod
    def is_language_supported(self, language_code: str) -> bool:
        """Return True if this detector can confidently handle the language."""
        ...
