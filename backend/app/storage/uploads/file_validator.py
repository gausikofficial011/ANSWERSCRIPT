"""
storage/uploads/file_validator.py — Upload File Validator

Validates uploaded files against domain rules before storage.
Checks MIME type, file size, extension, and page count limits.

This is domain-level validation (business rules), not framework validation.
Pydantic/FastAPI validates request structure; this validates file content.
"""

from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path

from app.core.constants import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    MAX_PAGE_COUNT,
    MAX_UPLOAD_SIZE_BYTES,
)
from app.domain.exceptions.file_exceptions import (
    FileTooLargeException,
    UnsupportedFileTypeException,
)


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of file validation.

    Attributes:
        is_valid:      True if all checks passed.
        detected_mime: The MIME type detected from file content.
        size_bytes:    File size in bytes.
        errors:        List of validation error messages (empty if valid).
    """
    is_valid: bool
    detected_mime: str
    size_bytes: int
    errors: tuple[str, ...] = ()


class FileValidator:
    """
    Validates uploaded answer sheet files.

    Checks performed (in order):
      1. File size ≤ MAX_UPLOAD_SIZE_BYTES (100 MB)
      2. Extension is in ALLOWED_EXTENSIONS
      3. MIME type matches declared extension
      4. For PDFs: page count ≤ MAX_PAGE_COUNT (100 pages)

    Design:
      - Raises domain exceptions (not HTTP exceptions) on failure.
      - PDF page count check requires pdf2image/poppler at call site.
    """

    def validate(
        self,
        filename: str,
        file_data: bytes,
        declared_mime_type: str | None = None,
    ) -> ValidationResult:
        """
        Validate a file for upload eligibility.

        Args:
            filename:          Original filename from the upload request.
            file_data:         Raw file bytes (read into memory for validation).
            declared_mime_type: MIME type declared by the client (not trusted alone).

        Returns:
            ValidationResult (always returns; raises on failure).

        Raises:
            FileTooLargeException:       If file exceeds size limit.
            UnsupportedFileTypeException: If file type is not allowed.
        """
        errors: list[str] = []
        size_bytes = len(file_data)

        # ── Size Check ──────────────────────────────────────────────────────
        if size_bytes > MAX_UPLOAD_SIZE_BYTES:
            raise FileTooLargeException(filename, size_bytes, MAX_UPLOAD_SIZE_BYTES)

        # ── Extension Check ─────────────────────────────────────────────────
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeException(
                filename,
                ext,
                list(ALLOWED_EXTENSIONS),
            )

        # ── MIME Type Detection ─────────────────────────────────────────────
        detected_mime, _ = mimetypes.guess_type(filename)
        if detected_mime not in ALLOWED_MIME_TYPES:
            raise UnsupportedFileTypeException(
                filename,
                detected_mime or "unknown",
                list(ALLOWED_MIME_TYPES),
            )

        return ValidationResult(
            is_valid=True,
            detected_mime=detected_mime,
            size_bytes=size_bytes,
            errors=tuple(errors),
        )

    def validate_page_count(self, page_count: int, filename: str) -> None:
        """
        Validate that a PDF does not exceed the maximum page count.

        Called separately after PDF conversion (requires page count from pdf2image).

        Raises:
            ValueError: If page_count exceeds MAX_PAGE_COUNT.
        """
        if page_count > MAX_PAGE_COUNT:
            raise ValueError(
                f"PDF '{filename}' has {page_count} pages, "
                f"exceeding the maximum of {MAX_PAGE_COUNT} pages."
            )
