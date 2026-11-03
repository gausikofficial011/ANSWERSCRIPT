"""
infrastructure/ocr/easyocr_service.py — EasyOCR Adapter Service
Enhanced with 2D spatial layout reconstruction and lexical artifact repair.
"""

from __future__ import annotations

import re
import time
import easyocr
from app.config import get_settings


class EasyOCRService:
    """
    Adapter service wrapping EasyOCR for text and coordinate extraction.
    Features lazy initialization, 2D line layout reconstruction, and lexical post-processing.
    """

    def __init__(self):
        self._reader = None
        self.settings = get_settings()

    @property
    def reader(self) -> easyocr.Reader:
        """Lazily initialize the easyocr.Reader instance."""
        if self._reader is None:
            gpu_enabled = getattr(self.settings, "ocr_gpu_enabled", False)
            self._reader = easyocr.Reader(["en"], gpu=gpu_enabled)
        return self._reader

    def extract_text(self, image_path: str, page_number: int) -> dict:
        """
        Runs EasyOCR on an image page.
        Extracts words, confidence, coordinates, and versioning.
        Applies 2D reading-order line reconstruction for accurate formatting.
        """
        start_time = time.time()

        # Run OCR
        results = self.reader.readtext(image_path)

        processing_time = time.time() - start_time
        threshold = self.settings.ocr_confidence_threshold  # Default is 0.50

        bounding_boxes = []
        total_confidence = 0.0
        words_count = len(results)
        page_low_confidence = False

        for bbox, text, confidence in results:
            x1 = int(bbox[0][0])
            y1 = int(bbox[0][1])
            x2 = int(bbox[2][0])
            y2 = int(bbox[2][1])

            confidence = float(confidence)
            block_low_confidence = confidence < threshold
            if block_low_confidence:
                page_low_confidence = True

            bounding_boxes.append({
                "text": text.strip(),
                "confidence": confidence,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "page_number": page_number,
                "low_confidence_flag": block_low_confidence
            })

            total_confidence += confidence

        average_confidence = (total_confidence / words_count) if words_count > 0 else 1.0
        if average_confidence < threshold:
            page_low_confidence = True

        # Reconstruct text with 2D spatial line clustering
        extracted_text = self._reconstruct_spatial_layout(bounding_boxes)

        # Apply lexical repair
        cleaned_text = self._clean_and_repair_text(extracted_text)

        return {
            "extracted_text": cleaned_text,
            "bounding_boxes": bounding_boxes,
            "average_confidence": round(average_confidence, 4),
            "words_detected": words_count,
            "low_confidence_flag": page_low_confidence,
            "ocr_engine_version": f"easyocr-{easyocr.__version__}",
            "preprocessing_version": "opencv-clahe-v2",
            "processing_time": processing_time
        }

    def _reconstruct_spatial_layout(self, boxes: list[dict]) -> str:
        """
        Groups bounding boxes into natural horizontal lines and orders them top-to-bottom,
        left-to-right.
        """
        if not boxes:
            return ""

        # Sort all boxes primarily by vertical center
        boxes_sorted = sorted(boxes, key=lambda b: ((b["y1"] + b["y2"]) / 2, b["x1"]))
        lines: list[list[dict]] = []
        current_line: list[dict] = []
        current_y_center: float | None = None

        for b in boxes_sorted:
            y_center = (b["y1"] + b["y2"]) / 2.0
            box_height = max(b["y2"] - b["y1"], 12)

            if current_y_center is None:
                current_line.append(b)
                current_y_center = y_center
            elif abs(y_center - current_y_center) < (box_height * 0.65):
                current_line.append(b)
                current_y_center = sum((item["y1"] + item["y2"]) / 2.0 for item in current_line) / len(current_line)
            else:
                current_line.sort(key=lambda item: item["x1"])
                lines.append(current_line)
                current_line = [b]
                current_y_center = y_center

        if current_line:
            current_line.sort(key=lambda item: item["x1"])
            lines.append(current_line)

        lines.sort(key=lambda line: (line[0]["y1"] + line[0]["y2"]) / 2.0)
        return "\n".join(" ".join(b["text"] for b in line) for line in lines)

    @staticmethod
    def _clean_and_repair_text(text: str) -> str:
        """
        Repairs common OCR recognition errors and word boundary issues.
        """
        if not text:
            return ""

        # 1. Unicode Ligature & Dash Replacements
        ligatures = {
            "\uFB01": "fi", "\uFB02": "fl", "\uFB00": "ff", "\uFB03": "ffi", "\uFB04": "ffl",
            "\u00A0": " ", "\u00AD": "", "\u201C": '"', "\u201D": '"', "\u2018": "'", "\u2019": "'",
            "\u2014": " - ", "\u2013": " - "
        }
        for k, v in ligatures.items():
            text = text.replace(k, v)

        # 2. Rejoin line-wrapped hyphenated words: data-\nstructure -> datastructure
        text = re.sub(r'(\b[a-zA-Z]+)-\s*\n\s*([a-zA-Z]+\b)', r'\1\2', text)

        # 3. Fix words glued to numbers: Question1 -> Question 1, 10Marks -> 10 Marks
        text = re.sub(r'([a-zA-Z]+)(\d+)', r'\1 \2', text)
        text = re.sub(r'(\d+)([a-zA-Z]+)', r'\1 \2', text)

        # 4. Fix CamelCase accidental joins: DefineStack -> Define Stack
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

        # 5. Fix common OCR misrecognitions
        ocr_fixes = {
            r'\bDetine\b': 'Define',
            r'\bDetne\b': 'Define',
            r'\bAnsier\b': 'Answer',
            r'\bAnsver\b': 'Answer',
            r'\bcichitectume\b': 'architecture',
            r'\binfromation\b': 'information',
            r'\binfomation\b': 'information',
            r'\brespones\b': 'responses',
            r'\bQucstion\b': 'Question',
            r'\bExplayn\b': 'Explain',
            r'\bExplaim\b': 'Explain',
            r'\bDitference\b': 'Difference',
            r'\bclientandserver\b': 'client and server',
            r'\bdata structure\b': 'Data Structure',
        }
        for pat, rep in ocr_fixes.items():
            text = re.sub(pat, rep, text, flags=re.IGNORECASE)

        # 6. Normalize whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
