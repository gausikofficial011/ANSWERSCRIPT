"""
ocr/extractors/text_block.py — TextBlock Data Model

Represents a single unit of text extracted by the OCR engine,
along with its position, confidence, and page metadata.

This is a pure data model — no OCR library dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BoundingBox:
    """
    Rectangular bounding box for an extracted text region.

    Coordinates are in pixels relative to the page image (top-left origin).

    Attributes:
        x:      Left edge pixel coordinate.
        y:      Top edge pixel coordinate.
        width:  Box width in pixels.
        height: Box height in pixels.
    """
    x: float
    y: float
    width: float
    height: float

    @classmethod
    def from_easyocr(cls, bbox: list[list[float]]) -> "BoundingBox":
        """
        Parse EasyOCR bounding box format.

        EasyOCR returns: [[top_left], [top_right], [bottom_right], [bottom_left]]
        where each point is [x, y].
        """
        top_left = bbox[0]
        bottom_right = bbox[2]
        x = top_left[0]
        y = top_left[1]
        width = bottom_right[0] - top_left[0]
        height = bottom_right[1] - top_left[1]
        return cls(x=x, y=y, width=width, height=height)

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}


@dataclass
class TextBlock:
    """
    A single unit of OCR-extracted text.

    Attributes:
        text:        The extracted text string (pre-normalization).
        bbox:        Bounding box within the page image.
        confidence:  OCR engine confidence in [0.0, 1.0].
        page_number: 1-based page number within the answer sheet.
        block_index: Ordering index within the page (top-to-bottom, left-to-right).
        language:    Detected language for this block (if per-block detection is used).
    """
    text: str
    bbox: BoundingBox
    confidence: float
    page_number: int
    block_index: int
    language: str = "en"

    @property
    def is_confident(self) -> bool:
        """True if confidence meets the system minimum threshold (0.6)."""
        from app.core.constants import OCR_MIN_CONFIDENCE
        return self.confidence >= OCR_MIN_CONFIDENCE

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "bbox": self.bbox.to_dict(),
            "confidence": self.confidence,
            "page_number": self.page_number,
            "block_index": self.block_index,
            "language": self.language,
        }


@dataclass
class PageOCRResult:
    """
    All OCR data extracted from a single page of an answer sheet.

    Attributes:
        page_number:        1-based page number.
        blocks:             All text blocks found on this page.
        page_width_px:      Page image width in pixels.
        page_height_px:     Page image height in pixels.
        overall_confidence: Mean confidence across all blocks.
    """
    page_number: int
    blocks: list[TextBlock] = field(default_factory=list)
    page_width_px: int = 0
    page_height_px: int = 0

    @property
    def full_text(self) -> str:
        """Concatenate all block texts in reading order."""
        return "\n".join(b.text for b in self.blocks if not b.is_empty)

    @property
    def overall_confidence(self) -> float:
        confident_blocks = [b for b in self.blocks if not b.is_empty]
        if not confident_blocks:
            return 0.0
        return sum(b.confidence for b in confident_blocks) / len(confident_blocks)

    @property
    def low_confidence_count(self) -> int:
        return sum(1 for b in self.blocks if not b.is_confident and not b.is_empty)
