"""
ai/multilingual/text_normalizer.py — Language-Specific Text Normalization

Normalizes OCR-extracted text per language before embedding.
Handles Unicode normalization, whitespace, and script-specific rules.

Normalization steps applied (in order):
  1. Unicode NFC normalization (canonical decomposition + composition)
  2. Whitespace normalization (collapse multiple spaces, strip)
  3. Script-specific rules (RTL markers, Indic ZWNJ handling)
  4. OCR artifact removal (common OCR noise patterns)
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


# ── OCR Artifact Patterns ─────────────────────────────────────────────────────
# Common OCR noise that should be cleaned before evaluation

_OCR_ARTIFACTS = re.compile(
    r"[|}{\\<>~`^*]+|"    # Symbol noise from OCR
    r"\s{3,}",             # Excessive whitespace
    re.UNICODE,
)

_MULTIPLE_SPACES = re.compile(r" {2,}")
_MULTIPLE_NEWLINES = re.compile(r"\n{3,}")


@dataclass(frozen=True)
class NormalizationConfig:
    """
    Configuration for text normalization behavior.

    Attributes:
        remove_ocr_artifacts:    Strip common OCR symbol noise.
        normalize_whitespace:    Collapse multiple spaces to single.
        unicode_form:            Unicode normalization form (NFC recommended).
        max_length_chars:        Truncate text exceeding this length.
                                 0 = no truncation.
    """
    remove_ocr_artifacts: bool = True
    normalize_whitespace: bool = True
    unicode_form: str = "NFC"
    max_length_chars: int = 10_000


class TextNormalizer:
    """
    Language-aware text normalizer for OCR output.

    Design:
      - Stateless: safe to call from multiple threads/workers.
      - Language-specific rules applied via _LANGUAGE_RULES registry.
    """

    # Language-specific normalization callbacks
    # Format: { "language_code": callable(text) -> text }
    _LANGUAGE_RULES: dict[str, list] = {
        "ar": [],   # Future: Arabic-specific normalization
        "hi": [],   # Future: Devanagari-specific normalization
        "ta": [],   # Future: Tamil-specific normalization
        "te": [],   # Future: Telugu-specific normalization
    }

    def normalize(
        self,
        text: str,
        language_code: str = "en",
        config: NormalizationConfig | None = None,
    ) -> str:
        """
        Apply full normalization pipeline to the input text.

        Args:
            text:          Raw OCR-extracted text.
            language_code: ISO 639-1 code for language-specific rules.
            config:        Normalization configuration (defaults used if None).

        Returns:
            Normalized text string.
        """
        if not text:
            return ""

        cfg = config or NormalizationConfig()

        # Step 1: Unicode normalization
        result = unicodedata.normalize(cfg.unicode_form, text)

        # Step 2: OCR artifact removal
        if cfg.remove_ocr_artifacts:
            result = _OCR_ARTIFACTS.sub(" ", result)

        # Step 3: Whitespace normalization
        if cfg.normalize_whitespace:
            result = _MULTIPLE_SPACES.sub(" ", result)
            result = _MULTIPLE_NEWLINES.sub("\n\n", result)
            result = result.strip()

        # Step 4: Language-specific rules
        for rule_fn in self._LANGUAGE_RULES.get(language_code, []):
            result = rule_fn(result)

        # Step 5: Length truncation
        if cfg.max_length_chars > 0:
            result = result[:cfg.max_length_chars]

        return result
