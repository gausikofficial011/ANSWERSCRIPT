"""
infrastructure/storage/file_metadata_service.py — File Metadata and Corruption Check Service
"""

from __future__ import annotations

import hashlib
import io
import re
import mimetypes
from pathlib import Path
from app.domain.exceptions.file_exceptions import CorruptedFileException


class FileMetadataService:
    """
    Extracts metadata from files and runs byte-level integrity checks.
    """

    def calculate_sha256(self, file_data: bytes) -> str:
        """Compute SHA256 hash of file data."""
        return hashlib.sha256(file_data).hexdigest()

    def detect_mime_type(self, filename: str) -> str:
        """Detect MIME type from file extension."""
        ext = Path(filename).suffix.lower()
        mime, _ = mimetypes.guess_type(filename)
        if ext in (".jpg", ".jpeg") and not mime:
            return "image/jpeg"
        return mime or "application/octet-stream"

    def extract_page_count(self, file_data: bytes, filename: str) -> int | None:
        """Extract page count for PDFs (returns None for images)."""
        mime = self.detect_mime_type(filename)
        if mime != "application/pdf":
            return None

        # Try using pypdf if installed
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_data))
            return len(reader.pages)
        except Exception:
            # Fallback regex search for PDF page objects
            # Standard PDF pages are declared via /Type /Page
            pages = re.findall(rb'/Type\s*/Page\b', file_data)
            if pages:
                return len(pages)
            return 1

    def verify_integrity(self, file_data: bytes, filename: str) -> None:
        """
        Verify that the file is not corrupted or empty.
        Raises CorruptedFileException if checks fail.
        """
        mime = self.detect_mime_type(filename)
        
        # 1. Check PDF integrity
        if mime == "application/pdf":
            # PDF header check
            if not file_data.startswith(b"%PDF-"):
                raise CorruptedFileException(filename, "Invalid PDF header signature")
            
            # Try reading it with pypdf to verify it isn't malformed
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(file_data))
                if len(reader.pages) == 0:
                    raise ValueError("PDF has 0 pages")
            except Exception as e:
                # If pypdf is installed and failed, raise. Otherwise, we trust header if pypdf import failed.
                if "PdfReader" in globals() or "pypdf" in globals():
                    raise CorruptedFileException(filename, f"Malformed PDF structure: {str(e)}")

        # 2. Check Image integrity (PNG, JPEG)
        elif mime.startswith("image/"):
            # Pillow validation
            try:
                from PIL import Image
                img = Image.open(io.BytesIO(file_data))
                img.verify()
            except ImportError:
                # Fallback signature checks if Pillow isn't available
                if mime == "image/png":
                    if not file_data.startswith(b"\x89PNG\r\n\x1a\n"):
                        raise CorruptedFileException(filename, "Invalid PNG magic numbers")
                elif mime == "image/jpeg":
                    if not file_data.startswith(b"\xff\xd8\xff"):
                        raise CorruptedFileException(filename, "Invalid JPEG magic numbers")
            except Exception as e:
                raise CorruptedFileException(filename, f"Invalid or corrupted image: {str(e)}")
