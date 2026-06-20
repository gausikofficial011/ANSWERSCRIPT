"""
domain/services/storage_lifecycle_service.py — Abstract Storage Lifecycle Service
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class StorageLifecycleService(ABC):
    """
    Abstract contract managing file locations and state across their lifecycle
    including archiving and failed upload sorting.
    """

    @abstractmethod
    async def archive_file(self, relative_path: str) -> str:
        """
        Move an existing file to the archive/ folder structure.

        Returns:
            The new relative path of the archived file.
        """
        ...

    @abstractmethod
    async def handle_failed_upload(self, relative_path: str) -> str:
        """
        Move an upload to failed_uploads/ in case of validation/parsing crash.

        Returns:
            The new relative path of the failed file.
        """
        ...
