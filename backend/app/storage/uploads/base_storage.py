"""
storage/uploads/base_storage.py — Abstract File Storage Interface

All storage backends must implement this interface.
The application layer and use cases depend ONLY on this abstraction.

Current implementations:
  local_storage.py → LocalFileStorage (filesystem)

Future implementations (drop-in replacements):
  s3_storage.py    → S3FileStorage (AWS S3 or compatible)
  gcs_storage.py   → GCSFileStorage (Google Cloud Storage)
  azure_storage.py → AzureBlobStorage (Azure Blob Storage)

To swap the backend:
  1. Create new class implementing BaseFileStorage
  2. Update app/dependencies.py DI binding
  3. Zero changes to application or domain layers
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StoredFile:
    """
    Metadata about a file that has been successfully stored.

    Attributes:
        stored_name:    UUID-based filename (never the original name).
        relative_path:  Path relative to storage root (for DB storage).
        absolute_path:  Full filesystem path (for local storage).
        public_url:     Public-facing URL (for cloud storage; None for local).
        size_bytes:     Actual stored file size.
        mime_type:      Detected MIME type.
    """
    stored_name: str
    relative_path: str
    absolute_path: str
    public_url: str | None
    size_bytes: int
    mime_type: str


class BaseFileStorage(ABC):
    """
    Abstract file storage backend.

    All methods are synchronous — async wrappers are provided by
    the infrastructure layer using asyncio.run_in_executor().
    """

    @abstractmethod
    def save(
        self,
        file_data: bytes,
        destination_path: str,
        filename: str,
        mime_type: str,
    ) -> StoredFile:
        """
        Save file bytes to the specified destination path.

        Args:
            file_data:        Raw file bytes.
            destination_path: Relative path within storage (e.g., "answer_sheets/2024/01/").
            filename:         UUID-based filename to use for storage.
            mime_type:        Validated MIME type.

        Returns:
            StoredFile with path and metadata.

        Raises:
            FileStorageException: If the file cannot be written.
        """
        ...

    @abstractmethod
    def get(self, relative_path: str) -> bytes:
        """
        Retrieve file bytes by relative path.

        Raises:
            FileNotFoundException: If the file does not exist.
        """
        ...

    @abstractmethod
    def delete(self, relative_path: str) -> bool:
        """
        Delete a file by relative path.

        Returns:
            True if found and deleted, False if not found.
        """
        ...

    @abstractmethod
    def exists(self, relative_path: str) -> bool:
        """Check if a file exists at the given relative path."""
        ...

    @abstractmethod
    def get_absolute_path(self, relative_path: str) -> str:
        """
        Return the absolute path for a given relative path.
        For cloud backends, returns the full URL.
        """
        ...

    @abstractmethod
    def list_files(self, directory_path: str) -> list[str]:
        """
        List all file relative paths within a directory.
        Used by lifecycle management for cleanup operations.
        """
        ...
