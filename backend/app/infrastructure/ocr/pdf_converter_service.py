"""
infrastructure/ocr/pdf_converter_service.py — PDF to Image Converter Service
"""

from __future__ import annotations

import os
from pathlib import Path
import uuid
from pdf2image import convert_from_path


class PDFConverterService:
    """
    Service responsible for converting PDF answer sheets into high-resolution PNG images.
    """

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.original_images_dir = self.upload_dir / "original_images"
        self.original_images_dir.mkdir(parents=True, exist_ok=True)

    def convert_pdf_to_images(self, pdf_path: str | Path, answer_sheet_id: uuid.UUID) -> list[str]:
        """
        Converts all pages of a PDF to high-resolution PNG files.

        Args:
            pdf_path: Path to the target PDF file on disk.
            answer_sheet_id: The UUID of the AnswerSheet.

        Returns:
            A list of paths to the saved page images.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")

        # Create sub-directory for this answer sheet
        sheet_original_dir = self.original_images_dir / str(answer_sheet_id)
        sheet_original_dir.mkdir(parents=True, exist_ok=True)

        # Convert PDF pages (defaulting to 200 DPI for reliable OCR readability)
        pages = convert_from_path(str(pdf_path), dpi=200, fmt="png")

        image_paths = []
        for idx, page in enumerate(pages):
            page_number = idx + 1
            output_path = sheet_original_dir / f"page_{page_number}.png"
            page.save(str(output_path), "PNG")
            image_paths.append(str(output_path))

        return image_paths
