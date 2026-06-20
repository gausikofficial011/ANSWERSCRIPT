"""
infrastructure/ocr/easyocr_service.py — EasyOCR Adapter Service
"""

from __future__ import annotations

import time
import easyocr
from app.config import get_settings


class EasyOCRService:
    """
    Adapter service wrapping EasyOCR for text and coordinate extraction.
    Features lazy initialization and standardized bounding box structures.
    """

    def __init__(self):
        self._reader = None
        self.settings = get_settings()

    @property
    def reader(self) -> easyocr.Reader:
        """Lazily initialize the easyocr.Reader instance."""
        if self._reader is None:
            # Load reader for English (can add multilingual support easily later)
            gpu_enabled = getattr(self.settings, "ocr_gpu_enabled", False)
            # fallback if not defined: default to False
            self._reader = easyocr.Reader(["en"], gpu=gpu_enabled)
        return self._reader

    def extract_text(self, image_path: str, page_number: int) -> dict:
        """
        Runs EasyOCR on a preprocessed image page.
        Extracts words, confidence, coordinates, and versioning.

        Args:
            image_path: Path to the preprocessed page image file.
            page_number: The page number of this image.

        Returns:
            A dictionary containing:
                - extracted_text (str)
                - bounding_boxes (list[dict])
                - average_confidence (float)
                - words_detected (int)
                - low_confidence_flag (bool)
                - ocr_engine_version (str)
                - preprocessing_version (str)
                - processing_time (float)
        """
        start_time = time.time()

        # Run OCR
        results = self.reader.readtext(image_path)

        processing_time = time.time() - start_time
        threshold = self.settings.ocr_confidence_threshold  # Default is 0.50

        bounding_boxes = []
        total_confidence = 0.0
        words_count = len(results)

        texts = []
        page_low_confidence = False

        for bbox, text, confidence in results:
            # bbox is in [[x1, y1], [x2, y2], [x3, y3], [x4, y4]] format
            x1 = int(bbox[0][0])
            y1 = int(bbox[0][1])
            x2 = int(bbox[2][0])
            y2 = int(bbox[2][1])

            confidence = float(confidence)
            block_low_confidence = confidence < threshold
            if block_low_confidence:
                page_low_confidence = True

            bounding_boxes.append({
                "text": text,
                "confidence": confidence,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "page_number": page_number,
                "low_confidence_flag": block_low_confidence
            })

            total_confidence += confidence
            texts.append(text)

        average_confidence = (total_confidence / words_count) if words_count > 0 else 1.0

        # Page-level low confidence flag check
        if average_confidence < threshold:
            page_low_confidence = True

        extracted_text = " ".join(texts)

        return {
            "extracted_text": extracted_text,
            "bounding_boxes": bounding_boxes,
            "average_confidence": average_confidence,
            "words_detected": words_count,
            "low_confidence_flag": page_low_confidence,
            "ocr_engine_version": f"easyocr-{easyocr.__version__}",
            "preprocessing_version": "opencv-1.0",
            "processing_time": processing_time
        }
