"""
tests/unit/application/test_upload_answer_sheet.py — Unit Tests for UploadAnswerSheetUseCase
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.application.use_cases.answer_sheets.upload_answer_sheet_use_case import UploadAnswerSheetUseCase
from app.application.use_cases.answer_sheets.delete_answer_sheet_use_case import DeleteAnswerSheetUseCase
from app.domain.entities.answer_sheet import AnswerSheet
from app.domain.entities.exam import Exam
from app.domain.entities.student import Student
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.student_repository import StudentRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.services.malware_scanner import MalwareScanner
from app.domain.services.student_mapping_service import StudentMappingService
from app.storage.uploads.base_storage import BaseFileStorage, StoredFile
from app.infrastructure.storage.file_validator_service import FileValidatorService
from app.infrastructure.storage.file_metadata_service import FileMetadataService

from app.domain.exceptions.domain_exception import (
    EntityNotFoundException,
    BusinessRuleViolationException,
)
from app.domain.exceptions.file_exceptions import (
    FileTooLargeException,
    UnsupportedFileTypeException,
    CorruptedFileException,
    EmptyFileException,
)
from app.core.constants import AnswerSheetStatus, AuditAction, AuditStatus


@pytest.fixture
def mock_answer_sheet_repo():
    repo = MagicMock(spec=AnswerSheetRepository)
    repo.save = AsyncMock()
    repo.delete = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_hash = AsyncMock()
    repo.get_by_student_and_exam = AsyncMock()
    return repo


@pytest.fixture
def mock_exam_repo():
    repo = MagicMock(spec=ExamRepository)
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_student_repo():
    repo = MagicMock(spec=StudentRepository)
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_audit_repo():
    repo = MagicMock(spec=AuditLogRepository)
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_storage():
    repo = MagicMock(spec=BaseFileStorage)
    repo.save = MagicMock()
    return repo


@pytest.fixture
def mock_scanner():
    scanner = MagicMock(spec=MalwareScanner)
    scanner.scan = AsyncMock(return_value=True)
    return scanner


@pytest.fixture
def mock_mapping_service():
    service = MagicMock(spec=StudentMappingService)
    service.map_student = AsyncMock()
    return service


@pytest.fixture
def validator_service():
    return FileValidatorService()


@pytest.fixture
def metadata_service():
    return FileMetadataService()


@pytest.mark.asyncio
async def test_upload_success_manual_student(
    mock_answer_sheet_repo,
    mock_exam_repo,
    mock_student_repo,
    mock_audit_repo,
    mock_storage,
    mock_scanner,
    mock_mapping_service,
    validator_service,
    metadata_service
):
    exam_id = uuid.uuid4()
    student_id = uuid.uuid4()
    uploader_id = uuid.uuid4()

    exam = Exam(
        id=exam_id,
        subject_id=uuid.uuid4(),
        title="Physics Midterm",
        exam_date=datetime.now().date(),
        total_marks=100,
        passing_marks=40,
        created_by=uploader_id
    )
    mock_exam_repo.get_by_id.return_value = exam

    mock_mapping_service.map_student.return_value = student_id
    mock_answer_sheet_repo.get_by_hash.return_value = None
    mock_answer_sheet_repo.get_by_student_and_exam.return_value = None

    stored_file = StoredFile(
        stored_name="uuid.pdf",
        relative_path="answer_sheets/exam/uuid.pdf",
        absolute_path="/app/uploads/answer_sheets/exam/uuid.pdf",
        public_url=None,
        size_bytes=1000,
        mime_type="application/pdf"
    )
    mock_storage.save.return_value = stored_file

    mock_answer_sheet_repo.save.side_effect = lambda sheet: sheet

    use_case = UploadAnswerSheetUseCase(
        answer_sheet_repo=mock_answer_sheet_repo,
        exam_repo=mock_exam_repo,
        student_repo=mock_student_repo,
        audit_repo=mock_audit_repo,
        storage_service=mock_storage,
        validator_service=validator_service,
        metadata_service=metadata_service,
        scanner=mock_scanner,
        mapping_service=mock_mapping_service
    )

    pdf_data = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF"
    # Patch Celery task dispatch to prevent eager execution inside async loop
    with patch("app.tasks.ocr_tasks.process_answer_sheet_ocr.delay") as mock_delay:
        sheet = await use_case.execute(
            exam_id=exam_id,
            filename="STU001.pdf",
            file_data=pdf_data,
            uploaded_by=uploader_id,
            manual_student_id=student_id
        )

    assert sheet.exam_id == exam_id
    assert sheet.student_id == student_id
    assert sheet.mime_type == "application/pdf"
    # file_size_bytes comes from stored_file.size_bytes, not raw pdf_data length
    assert sheet.file_size_bytes == stored_file.size_bytes
    # Use case transitions status to QUEUED_FOR_OCR after saving audit log
    assert sheet.status == AnswerSheetStatus.QUEUED_FOR_OCR

    mock_storage.save.assert_called_once()
    mock_scanner.scan.assert_called_once()
    mock_delay.assert_called_once_with(str(sheet.id))
    # audit_repo.save: (1) ANSWER_SHEET_UPLOADED success, (2) ANSWER_SHEET_QUEUED
    assert mock_audit_repo.save.call_count == 2
    # answer_sheet_repo.save: (1) initial save, (2) after queue status update
    assert mock_answer_sheet_repo.save.call_count == 2


@pytest.mark.asyncio
async def test_upload_malware_detected(
    mock_answer_sheet_repo,
    mock_exam_repo,
    mock_student_repo,
    mock_audit_repo,
    mock_storage,
    mock_scanner,
    mock_mapping_service,
    validator_service,
    metadata_service
):
    exam_id = uuid.uuid4()
    mock_scanner.scan.return_value = False  # Malware found

    use_case = UploadAnswerSheetUseCase(
        answer_sheet_repo=mock_answer_sheet_repo,
        exam_repo=mock_exam_repo,
        student_repo=mock_student_repo,
        audit_repo=mock_audit_repo,
        storage_service=mock_storage,
        validator_service=validator_service,
        metadata_service=metadata_service,
        scanner=mock_scanner,
        mapping_service=mock_mapping_service
    )

    mock_exam_repo.get_by_id.return_value = MagicMock()

    with pytest.raises(BusinessRuleViolationException) as exc_info:
        await use_case.execute(
            exam_id=exam_id,
            filename="infected.pdf",
            file_data=b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF",
            uploaded_by=uuid.uuid4()
        )

    assert "Malware scan failed" in exc_info.value.rule
    mock_storage.save.assert_not_called()


@pytest.mark.asyncio
async def test_upload_corrupted_pdf(
    mock_answer_sheet_repo,
    mock_exam_repo,
    mock_student_repo,
    mock_audit_repo,
    mock_storage,
    mock_scanner,
    mock_mapping_service,
    validator_service,
    metadata_service
):
    use_case = UploadAnswerSheetUseCase(
        answer_sheet_repo=mock_answer_sheet_repo,
        exam_repo=mock_exam_repo,
        student_repo=mock_student_repo,
        audit_repo=mock_audit_repo,
        storage_service=mock_storage,
        validator_service=validator_service,
        metadata_service=metadata_service,
        scanner=mock_scanner,
        mapping_service=mock_mapping_service
    )

    mock_exam_repo.get_by_id.return_value = MagicMock()

    with pytest.raises(CorruptedFileException):
        await use_case.execute(
            exam_id=uuid.uuid4(),
            filename="corrupt.pdf",
            file_data=b"NOT_A_PDF_FORMAT_CONTENT",
            uploaded_by=uuid.uuid4()
        )


@pytest.mark.asyncio
async def test_upload_duplicate_submission_superseded(
    mock_answer_sheet_repo,
    mock_exam_repo,
    mock_student_repo,
    mock_audit_repo,
    mock_storage,
    mock_scanner,
    mock_mapping_service,
    validator_service,
    metadata_service
):
    exam_id = uuid.uuid4()
    student_id = uuid.uuid4()
    uploader_id = uuid.uuid4()
    old_sheet_id = uuid.uuid4()

    mock_exam_repo.get_by_id.return_value = MagicMock()
    mock_mapping_service.map_student.return_value = student_id
    mock_answer_sheet_repo.get_by_hash.return_value = None

    old_sheet = AnswerSheet(
        id=old_sheet_id,
        exam_id=exam_id,
        student_id=student_id,
        uploaded_by=uploader_id,
        original_filename="first_upload.pdf",
        stored_filename="old.pdf",
        file_path="relative/path/old.pdf",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash1",
        status=AnswerSheetStatus.UPLOADED,
        processing_status=AnswerSheetStatus.UPLOADED
    )
    mock_answer_sheet_repo.get_by_student_and_exam.return_value = old_sheet

    stored_file = StoredFile(
        stored_name="new.pdf",
        relative_path="relative/path/new.pdf",
        absolute_path="/abs/path/new.pdf",
        public_url=None,
        size_bytes=2000,
        mime_type="application/pdf"
    )
    mock_storage.save.return_value = stored_file
    mock_answer_sheet_repo.save.side_effect = lambda sheet: sheet

    use_case = UploadAnswerSheetUseCase(
        answer_sheet_repo=mock_answer_sheet_repo,
        exam_repo=mock_exam_repo,
        student_repo=mock_student_repo,
        audit_repo=mock_audit_repo,
        storage_service=mock_storage,
        validator_service=validator_service,
        metadata_service=metadata_service,
        scanner=mock_scanner,
        mapping_service=mock_mapping_service
    )

    # Patch Celery task dispatch to prevent eager execution inside async loop
    with patch("app.tasks.ocr_tasks.process_answer_sheet_ocr.delay") as mock_delay:
        new_sheet = await use_case.execute(
            exam_id=exam_id,
            filename="new_upload.pdf",
            file_data=b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF",
            uploaded_by=uploader_id
        )

    assert new_sheet.supersedes_answer_sheet_id == old_sheet_id
    assert old_sheet.status == AnswerSheetStatus.SUPERSEDED
    assert old_sheet.superseded_by_answer_sheet_id == new_sheet.id
    mock_delay.assert_called_once_with(str(new_sheet.id))
    # answer_sheet_repo.save: (1) new sheet initial, (2) old sheet SUPERSEDED, (3) new sheet QUEUED
    assert mock_answer_sheet_repo.save.call_count == 3
    # audit_repo.save: (1) ANSWER_SHEET_REPLACED, (2) ANSWER_SHEET_UPLOADED, (3) ANSWER_SHEET_QUEUED
    assert mock_audit_repo.save.call_count == 3


@pytest.mark.asyncio
async def test_delete_answer_sheet_success(mock_answer_sheet_repo, mock_audit_repo):
    sheet_id = uuid.uuid4()
    sheet = AnswerSheet(
        id=sheet_id,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="filename.pdf",
        stored_filename="stored.pdf",
        file_path="relative/path/stored.pdf",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash"
    )
    mock_answer_sheet_repo.get_by_id.return_value = sheet
    mock_answer_sheet_repo.delete.return_value = True

    use_case = DeleteAnswerSheetUseCase(
        answer_sheet_repo=mock_answer_sheet_repo,
        audit_repo=mock_audit_repo
    )

    result = await use_case.execute(answer_sheet_id=sheet_id, deleter_id=uuid.uuid4())
    
    assert result is True
    mock_answer_sheet_repo.delete.assert_called_once_with(sheet_id)
    mock_audit_repo.save.assert_called_once()
