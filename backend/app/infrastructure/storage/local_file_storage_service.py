"""
infrastructure/storage/local_file_storage_service.py — Local Filesystem Storage Service
"""

from __future__ import annotations

import os
from pathlib import Path
from app.config import get_settings
from app.storage.uploads.base_storage import BaseFileStorage, StoredFile
from app.domain.exceptions.file_exceptions import FileStorageException, FileNotFoundException


class LocalFileStorageService(BaseFileStorage):
    """
    Concrete file storage backend storing files directly to the local disk.
    """

    def __init__(self, upload_dir: str | None = None):
        self.base_dir = Path(upload_dir or get_settings().upload_dir).resolve()
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        file_data: bytes,
        destination_path: str,
        filename: str,
        mime_type: str,
    ) -> StoredFile:
        try:
            # Construct target path inside base uploads folder
            target_dir = (self.base_dir / destination_path).resolve()
            target_dir.mkdir(parents=True, exist_ok=True)
            
            target_file = target_dir / filename
            
            # Write raw bytes
            target_file.write_bytes(file_data)
            
            # Compute relative path and absolute path
            relative_filepath = str(Path(destination_path) / filename).replace("\\", "/")
            absolute_filepath = str(target_file.resolve()).replace("\\", "/")
            
            return StoredFile(
                stored_name=filename,
                relative_path=relative_filepath,
                absolute_path=absolute_filepath,
                public_url=None,
                size_bytes=len(file_data),
                mime_type=mime_type
            )
        except Exception as e:
            raise FileStorageException(filename, str(e))

    def get(self, relative_path: str) -> bytes:
        target_file = self.base_dir / relative_path
        if not target_file.exists() or not target_file.is_file():
            raise FileNotFoundException(relative_path)
        try:
            return target_file.read_bytes()
        except Exception as e:
            raise FileStorageException(relative_path, f"Read error: {str(e)}")

    def delete(self, relative_path: str) -> bool:
        target_file = self.base_dir / relative_path
        if not target_file.exists() or not target_file.is_file():
            return False
        try:
            target_file.unlink()
            return True
        except Exception:
            return False

    def exists(self, relative_path: str) -> bool:
        target_file = self.base_dir / relative_path
        return target_file.exists() and target_file.is_file()

    def get_absolute_path(self, relative_path: str) -> str:
        return str((self.base_dir / relative_path).resolve()).replace("\\", "/")

    def list_files(self, directory_path: str) -> list[str]:
        target_dir = self.base_dir / directory_path
        if not target_dir.exists() or not target_dir.is_dir():
            return []
        try:
            paths = []
            for root, _, files in os.walk(target_dir):
                for f in files:
                    full_path = Path(root) / f
                    rel_path = full_path.relative_to(self.base_dir)
                    paths.append(str(rel_path).replace("\\", "/"))
            return paths
        except Exception:
            return []
