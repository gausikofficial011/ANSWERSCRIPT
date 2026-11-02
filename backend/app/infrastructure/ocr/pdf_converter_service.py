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
        self.poppler_path = os.getenv("POPPLER_PATH") or self._detect_poppler_path()

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
            resolved_path = self.upload_dir / pdf_path
            if resolved_path.exists():
                pdf_path = resolved_path
            else:
                raise FileNotFoundError(f"PDF file not found at {pdf_path}")

        # Create sub-directory for this answer sheet
        sheet_original_dir = self.original_images_dir / str(answer_sheet_id)
        sheet_original_dir.mkdir(parents=True, exist_ok=True)

        image_paths = []
        # Attempt rendering using pypdfium2 (self-contained, no external binary needed)
        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(str(pdf_path))
            for idx in range(len(pdf)):
                page = pdf[idx]
                image = page.render(scale=200 / 72).to_pil()
                page_number = idx + 1
                output_path = sheet_original_dir / f"page_{page_number}.png"
                image.save(str(output_path), "PNG")
                image_paths.append(str(output_path))
            return image_paths
        except Exception:
            pass

        # Fallback to pdf2image / poppler
        pages = convert_from_path(str(pdf_path), dpi=200, fmt="png", poppler_path=self.poppler_path)

        for idx, page in enumerate(pages):
            page_number = idx + 1
            output_path = sheet_original_dir / f"page_{page_number}.png"
            page.save(str(output_path), "PNG")
            image_paths.append(str(output_path))

        return image_paths

    @staticmethod
    def _detect_poppler_path() -> str | None:
        """
        Auto-detect poppler binary directory from common Windows install locations.
        Falls back to None (rely on system PATH) if not found.
        """
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        winget_base = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_base.exists():
            for entry in sorted(winget_base.iterdir(), reverse=True):
                if "poppler" in entry.name.lower():
                    for binary in entry.rglob("pdftoppm.exe"):
                        return str(binary.parent)
        return None
