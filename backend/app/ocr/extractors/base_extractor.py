"""
ocr/extractors/base_extractor.py — Abstract OCR Extractor Interface

All OCR engine implementations must satisfy this interface.
This enables swapping EasyOCR for Tesseract, PaddleOCR, or
Google Cloud Vision without changing the application layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ocr.extractors.text_block import PageOCRResult


class BaseOCRExtractor(ABC):
    """
    Abstract interface for text extraction from prepared page images.

    Implementations receive a list of prepared image file paths
    (one per page, already enhanced by preprocessors) and return
    structured OCR results per page.

    Thread safety: Implementations must be safe for use in Celery workers.
    Model loading: Should happen at __init__ time; never per-call.
    """

    @abstractmethod
    def extract_page(
        self,
        image_path: str,
        page_number: int,
        languages: list[str],
    ) -> "PageOCRResult":
        """
        Extract text from a single preprocessed page image.

        Args:
            image_path:  Absolute path to the preprocessed page PNG.
            page_number: 1-based page number for metadata.
            languages:   ISO 639-1 language codes to attempt (e.g., ["en", "ta"]).

        Returns:
            PageOCRResult with all detected text blocks.
        """
        ...

    @abstractmethod
    def extract_pages(
        self,
        image_paths: list[str],
        languages: list[str],
    ) -> "list[PageOCRResult]":
        """
        Extract text from multiple page images sequentially.

        Args:
            image_paths: Ordered list of preprocessed page image paths.
            languages:   Languages to attempt on all pages.

        Returns:
            List of PageOCRResult, one per page, in page order.
        """
        ...

    @abstractmethod
    def supported_languages(self) -> list[str]:
        """Return ISO 639-1 codes this extractor can process."""
        ...

    @abstractmethod
    def engine_name(self) -> str:
        """Return the engine identifier (e.g., 'easyocr-1.7.1')."""
        ...
