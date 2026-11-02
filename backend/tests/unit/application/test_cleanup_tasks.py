"""
tests/unit/application/test_cleanup_tasks.py — Unit Tests for File Cleanup Celery Tasks
"""

from __future__ import annotations
import os
import uuid
import pytest
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.tasks.cleanup_tasks import (
    cleanup_temporary_files,
    cleanup_expired_reports,
    cleanup_job_temp_dir,
    REPORT_RETENTION_HOURS
)
from app.infrastructure.reports.report_registry import report_registry


@pytest.fixture
def mock_upload_dir(tmp_path):
    # Mock settings.upload_dir to point to pytest's tmp_path
    mock_settings = MagicMock()
    mock_settings.upload_dir = str(tmp_path)
    
    with patch("app.tasks.cleanup_tasks.get_settings", return_value=mock_settings):
        yield tmp_path


def test_cleanup_temporary_files(mock_upload_dir):
    temp_dir = mock_upload_dir / "temporary"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 1. Create a fresh file (should NOT be deleted)
    fresh_file = temp_dir / "fresh.txt"
    fresh_file.write_text("fresh")
    
    # 2. Create an expired file (should be deleted)
    expired_file = temp_dir / "expired.txt"
    expired_file.write_text("expired")
    
    # Modify mtime of expired file to 3 hours ago
    past_time = (datetime.now() - timedelta(hours=3)).timestamp()
    os.utime(expired_file, (past_time, past_time))

    res = cleanup_temporary_files()
    
    assert res["deleted_count"] == 1
    assert not expired_file.exists()
    assert fresh_file.exists()


def test_cleanup_temporary_files_missing_dir(mock_upload_dir):
    # If temporary dir doesn't exist, it should execute safely without exceptions
    res = cleanup_temporary_files()
    assert res["deleted_count"] == 0


def test_cleanup_expired_reports_registry():
    report_registry.clear()
    
    user_id = uuid.uuid4()
    # Register a fresh report (should NOT be removed)
    fresh_rep = report_registry.register(
        report_type="evaluation_report",
        requesting_user_id=user_id,
        file_size_bytes=500,
        metadata={}
    )
    
    # Register an expired report (should be removed)
    expired_rep = report_registry.register(
        report_type="plagiarism_report",
        requesting_user_id=user_id,
        file_size_bytes=1000,
        metadata={}
    )
    # Set generated_at to 25 hours ago
    expired_rep.generated_at = datetime.utcnow() - timedelta(hours=25)

    res = cleanup_expired_reports()
    
    assert res["deleted_count"] == 1
    assert len(report_registry.get_all()) == 1
    assert report_registry.get_by_id(fresh_rep.report_id) is not None
    assert report_registry.get_by_id(expired_rep.report_id) is None


def test_cleanup_job_temp_dir(mock_upload_dir):
    job_id = str(uuid.uuid4())
    job_temp_dir = mock_upload_dir / "temporary" / job_id
    job_temp_dir.mkdir(parents=True, exist_ok=True)

    # Add a nested directory structure
    sub_dir = job_temp_dir / "nested"
    sub_dir.mkdir(parents=True, exist_ok=True)
    
    file_1 = job_temp_dir / "file1.txt"
    file_1.write_text("hello")
    
    file_2 = sub_dir / "file2.txt"
    file_2.write_text("world")

    res = cleanup_job_temp_dir(job_id)
    
    # Check return values:
    # 2 files deleted: file1.txt, file2.txt
    # 2 directories deleted: nested/, job_id/
    assert res["job_id"] == job_id
    assert res["deleted_files"] == 2
    assert res["deleted_directories"] == 2
    
    assert not job_temp_dir.exists()


def test_cleanup_job_temp_dir_missing(mock_upload_dir):
    # Missing job temp dir should return zero counts and execute safely
    job_id = str(uuid.uuid4())
    res = cleanup_job_temp_dir(job_id)
    assert res["deleted_files"] == 0
    assert res["deleted_directories"] == 0
