"""
infrastructure/storage/local_storage_lifecycle_service.py — Local Lifecycle Management Service
"""

from __future__ import annotations

import shutil
from pathlib import Path
from app.config import get_settings
from app.domain.services.storage_lifecycle_service import StorageLifecycleService
from app.domain.exceptions.file_exceptions import FileNotFoundException, FileStorageException


class LocalStorageLifecycleService(StorageLifecycleService):
    """
    Concrete lifecycle service managing local directory structure.
    """

    def __init__(self, upload_dir: str | None = None):
        self.base_dir = Path(upload_dir or get_settings().upload_dir).resolve()

    async def archive_file(self, relative_path: str) -> str:
        """Move file to archive/ directory."""
        source_file = self.base_dir / relative_path
        if not source_file.exists():
            raise FileNotFoundException(relative_path)

        try:
            target_path = Path("archive") / relative_path
            dest_file = self.base_dir / target_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform atomic filesystem move
            shutil.move(str(source_file), str(dest_file))
            
            return str(target_path).replace("\\", "/")
        except Exception as e:
            raise FileStorageException(relative_path, f"Archive move failed: {str(e)}")

    async def handle_failed_upload(self, relative_path: str) -> str:
        """Move file to failed_uploads/ directory."""
        source_file = self.base_dir / relative_path
        if not source_file.exists():
            raise FileNotFoundException(relative_path)

        try:
            target_path = Path("failed_uploads") / relative_path
            dest_file = self.base_dir / target_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_file), str(dest_file))
            
            return str(target_path).replace("\\", "/")
        except Exception as e:
            raise FileStorageException(relative_path, f"Failed folder move failed: {str(e)}")
