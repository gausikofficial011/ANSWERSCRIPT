"""
infrastructure/storage/file_validator_service.py — File Validator Service
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from app.domain.exceptions.file_exceptions import (
    FileTooLargeException,
    UnsupportedFileTypeException,
    EmptyFileException,
    CorruptedFileException,
)

from app.config import get_settings

ALLOWED_EXTENSIONS = frozenset({".pdf", ".png", ".jpg", ".jpeg"})
ALLOWED_MIME_TYPES = frozenset({"application/pdf", "image/png", "image/jpeg"})


class FileValidatorService:
    """
    Validates file sizes, formats, extensions, and content constraints before storage.
    """

    def validate(self, filename: str, file_data: bytes) -> str:
        """
        Validate an uploaded file. Returns the resolved MIME type if valid, otherwise raises.
        """
        size_bytes = len(file_data)
        settings = get_settings()
        max_size = settings.max_upload_size_bytes
        
        # 1. Empty File Rejection
        if size_bytes == 0:
            raise EmptyFileException(filename)

        # 2. Size Constraint Rejection
        if size_bytes > max_size:
            raise FileTooLargeException(filename, size_bytes, max_size)


        # 3. Extension Rejection
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeException(filename, ext, list(ALLOWED_EXTENSIONS))

        # 4. MIME Type Rejection
        detected_mime, _ = mimetypes.guess_type(filename)
        # Normalize jpg to image/jpeg if needed
        if ext in (".jpg", ".jpeg") and not detected_mime:
            detected_mime = "image/jpeg"

        if detected_mime not in ALLOWED_MIME_TYPES:
            raise UnsupportedFileTypeException(
                filename,
                detected_mime or "unknown",
                list(ALLOWED_MIME_TYPES)
            )

        # 5. Magic Byte Signature Validation
        if detected_mime == "application/pdf":
            if not file_data.startswith(b"%PDF-"):
                raise CorruptedFileException(
                    filename,
                    "invalid PDF binary signature"
                )
        elif detected_mime == "image/png":
            if not file_data.startswith(b"\x89PNG"):
                raise CorruptedFileException(
                    filename,
                    "invalid PNG binary signature"
                )
        elif detected_mime == "image/jpeg":
            if not file_data.startswith(b"\xff\xd8\xff"):
                raise CorruptedFileException(
                    filename,
                    "invalid JPEG binary signature"
                )

        return detected_mime
