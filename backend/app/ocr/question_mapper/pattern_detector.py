"""
ocr/question_mapper/pattern_detector.py — Question Pattern Detector

Detects question boundaries in OCR text using regex patterns and
positional heuristics. Produces DetectedQuestion objects that
are later matched to DB Question entities.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ocr.extractors.text_block import TextBlock


@dataclass
class DetectedQuestion:
    """
    A question boundary detected in OCR output.

    Attributes:
        detected_number:   The question number as detected (e.g., 1, 2, 3).
        start_block_index: Index of the first TextBlock of this question.
        end_block_index:   Index of the last TextBlock of this question (-1 = end of page).
        page_number:       Page where this question starts.
        detection_method:  How this question was detected (for confidence scoring).
        confidence:        Detection confidence in [0.0, 1.0].
        text_blocks:       The TextBlock objects that belong to this question's answer.
    """
    detected_number: int
    start_block_index: int
    end_block_index: int
    page_number: int
    detection_method: str = "regex"   # "regex" | "positional" | "manual"
    confidence: float = 1.0
    text_blocks: list["TextBlock"] = field(default_factory=list)

    @property
    def answer_text(self) -> str:
        """Concatenate all answer text blocks for this question."""
        return "\n".join(b.text for b in self.text_blocks if not b.is_empty)

    @property
    def is_high_confidence(self) -> bool:
        from app.core.constants import OCR_QUESTION_MAP_HIGH
        return self.confidence >= OCR_QUESTION_MAP_HIGH

    @property
    def needs_review(self) -> bool:
        from app.core.constants import OCR_QUESTION_MAP_MEDIUM
        return self.confidence < OCR_QUESTION_MAP_MEDIUM


# ── Regex Patterns for Question Detection ────────────────────────────────────
# Listed in priority order (most specific first)

QUESTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"^Q(?:uestion)?\s*\.?\s*(\d+)\s*[.:\)]\s*", re.IGNORECASE),
    re.compile(r"^(\d+)\s*[.:\)]\s+", re.MULTILINE),
    re.compile(r"^(?:Part|Section)\s+[A-Z]\s*[-:]?\s*Q?\s*(\d+)", re.IGNORECASE),
    re.compile(r"^\((\d+)\)\s+", re.MULTILINE),
    re.compile(r"^(?:Ans|Answer)\s*\.?\s*(\d+)\s*[.:\)]\s*", re.IGNORECASE),
]
