"""
tests/unit/application/test_ocr_use_cases.py — Unit Tests for OCR Use Cases
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.domain.entities.answer_sheet import AnswerSheet
from app.domain.entities.ocr_result import OCRResult
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.ocr_result_repository import OCRResultRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.ocr.ocr_pipeline_service import OCRPipelineService

from app.application.use_cases.ocr.process_answer_sheet_ocr_use_case import ProcessAnswerSheetOCRUseCase
from app.application.use_cases.ocr.get_ocr_result_use_case import GetOCRResultUseCase
from app.application.use_cases.ocr.reprocess_ocr_use_case import ReprocessOCRUseCase
from app.core.constants import AnswerSheetStatus, OCRResultStatus
from app.domain.exceptions.domain_exception import EntityNotFoundException


@pytest.fixture
def mock_answer_sheet_repo():
    repo = MagicMock(spec=AnswerSheetRepository)
    repo.get_by_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_ocr_result_repo():
    repo = MagicMock(spec=OCRResultRepository)
    repo.save = AsyncMock()
    repo.list_by_answer_sheet_id = AsyncMock()
    repo.delete_by_answer_sheet_id = AsyncMock()
    return repo


@pytest.fixture
def mock_audit_repo():
    repo = MagicMock(spec=AuditLogRepository)
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_ocr_pipeline():
    pipeline = MagicMock(spec=OCRPipelineService)
    pipeline.process_answer_sheet = MagicMock()
    return pipeline


@pytest.mark.asyncio
async def test_process_ocr_use_case_success(
    mock_answer_sheet_repo,
    mock_ocr_result_repo,
    mock_audit_repo,
    mock_ocr_pipeline
):
    sheet_id = uuid.uuid4()
    sheet = AnswerSheet(
        id=sheet_id,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="student1.pdf",
        stored_filename="stored.pdf",
        file_path="uploads/stored.pdf",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.QUEUED_FOR_OCR,
        processing_status=AnswerSheetStatus.QUEUED_FOR_OCR
    )
    mock_answer_sheet_repo.get_by_id.return_value = sheet
    mock_answer_sheet_repo.save.side_effect = lambda s: s
    mock_ocr_result_repo.save.side_effect = lambda r: r

    # Mock pipeline returns 2 pages of OCR results
    mock_ocr_pipeline.process_answer_sheet.return_value = [
        {
            "page_number": 1,
            "extracted_text": "hello page one",
            "bounding_boxes": [{"text": "hello", "confidence": 0.9, "x1": 0, "y1": 0, "x2": 10, "y2": 10, "page_number": 1, "low_confidence_flag": False}],
            "average_confidence": 0.9,
            "words_detected": 1,
            "low_confidence_flag": False,
            "ocr_engine_version": "easyocr-1.0",
            "preprocessing_version": "opencv-1.0",
            "processing_time": 0.5
        },
        {
            "page_number": 2,
            "extracted_text": "low confidence test",
            "bounding_boxes": [{"text": "test", "confidence": 0.4, "x1": 0, "y1": 0, "x2": 10, "y2": 10, "page_number": 2, "low_confidence_flag": True}],
            "average_confidence": 0.4,
            "words_detected": 1,
            "low_confidence_flag": True,
            "ocr_engine_version": "easyocr-1.0",
            "preprocessing_version": "opencv-1.0",
            "processing_time": 0.6
        }
    ]

    use_case = ProcessAnswerSheetOCRUseCase(
        answer_sheet_repo=mock_answer_sheet_repo,
        ocr_result_repo=mock_ocr_result_repo,
        audit_repo=mock_audit_repo,
        ocr_pipeline=mock_ocr_pipeline
    )

    results = await use_case.execute(sheet_id)

    assert len(results) == 2
    assert results[0].page_number == 1
    assert results[0].status == OCRResultStatus.OCR_COMPLETED
    assert results[1].page_number == 2
    assert results[1].status == OCRResultStatus.OCR_LOW_CONFIDENCE

    assert sheet.status == AnswerSheetStatus.OCR_COMPLETED
    assert sheet.page_count == 2
    mock_ocr_result_repo.delete_by_answer_sheet_id.assert_called_once_with(sheet_id)
    assert mock_ocr_result_repo.save.call_count == 2
    assert mock_audit_repo.save.call_count == 2  # Start + Complete


@pytest.mark.asyncio
async def test_process_ocr_use_case_failure(
    mock_answer_sheet_repo,
    mock_ocr_result_repo,
    mock_audit_repo,
    mock_ocr_pipeline
):
    sheet_id = uuid.uuid4()
    sheet = AnswerSheet(
        id=sheet_id,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="student1.pdf",
        stored_filename="stored.pdf",
        file_path="uploads/stored.pdf",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.QUEUED_FOR_OCR,
        processing_status=AnswerSheetStatus.QUEUED_FOR_OCR
    )
    mock_answer_sheet_repo.get_by_id.return_value = sheet
    mock_ocr_pipeline.process_answer_sheet.side_effect = RuntimeError("PDF corrupted")

    use_case = ProcessAnswerSheetOCRUseCase(
        answer_sheet_repo=mock_answer_sheet_repo,
        ocr_result_repo=mock_ocr_result_repo,
        audit_repo=mock_audit_repo,
        ocr_pipeline=mock_ocr_pipeline
    )

    with pytest.raises(RuntimeError):
        await use_case.execute(sheet_id)

    assert sheet.status == AnswerSheetStatus.FAILED
    assert sheet.failure_reason == "PDF corrupted"
    assert mock_audit_repo.save.call_count == 2  # Start + Failure


@pytest.mark.asyncio
async def test_get_ocr_results_success(mock_answer_sheet_repo, mock_ocr_result_repo):
    sheet_id = uuid.uuid4()
    sheet = MagicMock(spec=AnswerSheet)
    mock_answer_sheet_repo.get_by_id.return_value = sheet

    dummy_results = [MagicMock(spec=OCRResult), MagicMock(spec=OCRResult)]
    mock_ocr_result_repo.list_by_answer_sheet_id.return_value = dummy_results

    use_case = GetOCRResultUseCase(
        answer_sheet_repo=mock_answer_sheet_repo,
        ocr_result_repo=mock_ocr_result_repo
    )

    res = await use_case.execute(sheet_id)
    assert res == dummy_results
    mock_ocr_result_repo.list_by_answer_sheet_id.assert_called_once_with(sheet_id)


@pytest.mark.asyncio
async def test_reprocess_ocr_use_case_success(
    mock_answer_sheet_repo,
    mock_ocr_result_repo,
    mock_audit_repo
):
    sheet_id = uuid.uuid4()
    sheet = AnswerSheet(
        id=sheet_id,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="student1.pdf",
        stored_filename="stored.pdf",
        file_path="uploads/stored.pdf",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash",
        status=AnswerSheetStatus.FAILED,
        processing_status=AnswerSheetStatus.FAILED
    )
    mock_answer_sheet_repo.get_by_id.return_value = sheet
    mock_answer_sheet_repo.save.side_effect = lambda s: s

    use_case = ReprocessOCRUseCase(
        answer_sheet_repo=mock_answer_sheet_repo,
        ocr_result_repo=mock_ocr_result_repo,
        audit_repo=mock_audit_repo,
        upload_dir="uploads"
    )

    with patch("shutil.rmtree") as mock_rmtree, \
         patch("app.tasks.ocr_tasks.process_answer_sheet_ocr.delay") as mock_delay:
        
        updated_sheet = await use_case.execute(sheet_id)

        assert updated_sheet.status == AnswerSheetStatus.QUEUED_FOR_OCR
        assert updated_sheet.failure_reason is None
        mock_ocr_result_repo.delete_by_answer_sheet_id.assert_called_once_with(sheet_id)
        mock_audit_repo.save.assert_called_once()
        mock_delay.assert_called_once_with(str(sheet_id), force_reprocess=True)
