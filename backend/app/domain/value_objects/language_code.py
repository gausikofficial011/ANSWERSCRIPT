"""
domain/value_objects/language_code.py — Language Code Value Object

Represents a validated ISO 639-1 language code.
EasyOCR and SentenceTransformers both use ISO 639-1 codes.
"""

from __future__ import annotations

from dataclasses import dataclass

# Supported language codes — expand as new OCR/embedding models are added
_SUPPORTED_LANGUAGE_CODES: frozenset[str] = frozenset({
    "en",   # English
    "ta",   # Tamil
    "hi",   # Hindi
    "te",   # Telugu
    "kn",   # Kannada
    "ml",   # Malayalam
    "fr",   # French
    "ar",   # Arabic
    "zh",   # Chinese (Simplified)  — EasyOCR code: ch_sim
    "ja",   # Japanese
    "de",   # German
    "es",   # Spanish
    "pt",   # Portuguese
    "ru",   # Russian
    "ko",   # Korean
})


@dataclass(frozen=True)
class LanguageCode:
    """
    ISO 639-1 language code value object.

    Invariants:
      - Must be a 2-letter lowercase code.
      - Must be in the system's supported language set.

    Usage:
      lang = LanguageCode("en")
      lang.is_rtl  → False

      LanguageCode("xx")  → raises ValueError
    """

    code: str

    def __post_init__(self) -> None:
        normalized = self.code.strip().lower()
        object.__setattr__(self, "code", normalized)
        self._validate()

    def _validate(self) -> None:
        if len(self.code) != 2:
            raise ValueError(
                f"Language code must be a 2-character ISO 639-1 code, got '{self.code}'."
            )
        if self.code not in _SUPPORTED_LANGUAGE_CODES:
            raise ValueError(
                f"Language '{self.code}' is not supported. "
                f"Supported: {sorted(_SUPPORTED_LANGUAGE_CODES)}"
            )

    @property
    def is_rtl(self) -> bool:
        """Return True for right-to-left languages."""
        return self.code in {"ar", "he", "fa", "ur"}

    @property
    def is_indic(self) -> bool:
        """Return True for Indic script languages."""
        return self.code in {"hi", "ta", "te", "kn", "ml"}

    @classmethod
    def english(cls) -> "LanguageCode":
        return cls("en")

    @classmethod
    def supported_codes(cls) -> frozenset[str]:
        return _SUPPORTED_LANGUAGE_CODES

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return f"LanguageCode('{self.code}')"
