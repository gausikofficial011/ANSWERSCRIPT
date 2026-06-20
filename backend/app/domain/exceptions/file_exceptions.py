"""domain/exceptions/file_exceptions.py — File Handling Domain Exceptions"""

from app.domain.exceptions.domain_exception import DomainException


class FileException(DomainException):
    """Base for all file-related domain failures."""


class FileTooLargeException(FileException):
    """Raised when an uploaded file exceeds the maximum allowed size."""

    def __init__(self, filename: str, size_bytes: int, max_bytes: int) -> None:
        max_mb = max_bytes // (1024 * 1024)
        actual_mb = size_bytes / (1024 * 1024)
        super().__init__(
            message=(
                f"File '{filename}' ({actual_mb:.1f} MB) exceeds the maximum "
                f"allowed size of {max_mb} MB."
            ),
            context={
                "filename": filename,
                "size_bytes": size_bytes,
                "max_bytes": max_bytes,
            },
        )


class UnsupportedFileTypeException(FileException):
    """Raised when an uploaded file's MIME type is not in the allowed set."""

    def __init__(self, filename: str, detected_mime: str, allowed: list[str]) -> None:
        super().__init__(
            message=(
                f"File '{filename}' has unsupported type '{detected_mime}'. "
                f"Allowed types: {', '.join(allowed)}."
            ),
            context={
                "filename": filename,
                "detected_mime": detected_mime,
                "allowed_types": allowed,
            },
        )


class FileStorageException(FileException):
    """Raised when a file cannot be saved to the storage backend."""

    def __init__(self, filename: str, reason: str) -> None:
        super().__init__(
            message=f"Failed to store file '{filename}': {reason}",
            context={"filename": filename, "reason": reason},
        )


class FileNotFoundException(FileException):
    """Raised when a requested file does not exist in storage."""

    def __init__(self, file_path: str) -> None:
        super().__init__(
            message=f"File not found at path: '{file_path}'",
            context={"file_path": file_path},
        )


class CorruptedFileException(FileException):
    """Raised when an uploaded file is corrupted or unreadable."""

    def __init__(self, filename: str, reason: str = "Corrupted format") -> None:
        super().__init__(
            message=f"File '{filename}' is corrupted or unreadable: {reason}.",
            context={"filename": filename, "reason": reason},
        )


class EmptyFileException(FileException):
    """Raised when an uploaded file contains 0 bytes."""

    def __init__(self, filename: str) -> None:
        super().__init__(
            message=f"File '{filename}' contains no data (empty file).",
            context={"filename": filename},
        )
