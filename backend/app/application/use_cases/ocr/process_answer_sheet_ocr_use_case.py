"""
application/use_cases/ocr/process_answer_sheet_ocr_use_case.py — Process OCR Use Case
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
import uuid

from app.domain.entities.ocr_result import OCRResult
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.ocr_result_repository import OCRResultRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.ocr.ocr_pipeline_service import OCRPipelineService
from app.core.constants import AnswerSheetStatus, OCRResultStatus, AuditAction, AuditStatus
from app.domain.exceptions.domain_exception import EntityNotFoundException

logger = logging.getLogger(__name__)


class ProcessAnswerSheetOCRUseCase:
    """
    Use case responsible for running the OCR processing pipeline on an AnswerSheet,
    handling state updates, error logging, and audit logs.
    """

    def __init__(
        self,
        answer_sheet_repo: AnswerSheetRepository,
        ocr_result_repo: OCRResultRepository,
        audit_repo: AuditLogRepository,
        ocr_pipeline: OCRPipelineService
    ):
        self.answer_sheet_repo = answer_sheet_repo
        self.ocr_result_repo = ocr_result_repo
        self.audit_repo = audit_repo
        self.ocr_pipeline = ocr_pipeline

    async def execute(
        self,
        answer_sheet_id: uuid.UUID,
        user_id: uuid.UUID | None = None
    ) -> list[OCRResult]:
        """
        Orchestrates OCR extraction:
        1. Fetch answer sheet.
        2. Set status to OCR_PROCESSING.
        3. Clear old OCR results for idempotency.
        4. Run OCR pipeline.
        5. Persist page-wise OCRResult entities.
        6. Set status to OCR_COMPLETED (or FAILED if exceptions occur).

        Args:
            answer_sheet_id: UUID of the AnswerSheet to process.
            user_id: UUID of the user triggering (system if None).
        """
        now = datetime.now(timezone.utc)
        user_id = user_id or uuid.UUID("00000000-0000-0000-0000-000000000000")  # Default to system UUID

        # 1. Fetch AnswerSheet
        sheet = await self.answer_sheet_repo.get_by_id(answer_sheet_id)
        if not sheet:
            raise EntityNotFoundException(entity_type="AnswerSheet", entity_id=answer_sheet_id)

        # 2. Update status to OCR_PROCESSING
        sheet.status = AnswerSheetStatus.OCR_PROCESSING
        sheet.processing_status = AnswerSheetStatus.OCR_PROCESSING
        sheet.processing_started_at = now
        sheet.updated_at = now
        await self.answer_sheet_repo.save(sheet)

        # Log audit for starting OCR
        start_log = AuditLog(
            action=AuditAction.OCR_TRIGGERED,
            resource_type="answer_sheets",
            resource_id=answer_sheet_id,
            status=AuditStatus.SUCCESS,
            user_id=user_id,
            new_values={"status": AnswerSheetStatus.OCR_PROCESSING.value}
        )
        await self.audit_repo.save(start_log)

        try:
            # 3. Clear old OCR records
            await self.ocr_result_repo.delete_by_answer_sheet_id(answer_sheet_id)

            # 4. Execute pipeline
            page_results = self.ocr_pipeline.process_answer_sheet(sheet.file_path, answer_sheet_id)

            # 5. Persist OCRResult entities
            saved_results = []
            for p_res in page_results:
                ocr_status = OCRResultStatus.OCR_LOW_CONFIDENCE if p_res["low_confidence_flag"] else OCRResultStatus.OCR_COMPLETED

                ocr_result = OCRResult(
                    id=uuid.uuid4(),
                    answer_sheet_id=answer_sheet_id,
                    page_number=p_res["page_number"],
                    extracted_text=p_res["extracted_text"],
                    bounding_boxes=p_res["bounding_boxes"],
                    low_confidence_flag=p_res["low_confidence_flag"],
                    confidence_score=p_res["average_confidence"],
                    average_confidence=p_res["average_confidence"],
                    words_detected=p_res["words_detected"],
                    processing_time=p_res["processing_time"],
                    ocr_engine_version=p_res["ocr_engine_version"],
                    preprocessing_version=p_res["preprocessing_version"],
                    original_image_path=p_res.get("original_image_path", ""),
                    processed_image_path=p_res.get("processed_image_path", ""),
                    status=ocr_status,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                saved = await self.ocr_result_repo.save(ocr_result)
                saved_results.append(saved)

            # 6. Update AnswerSheet to OCR_COMPLETED
            sheet.status = AnswerSheetStatus.OCR_COMPLETED
            sheet.processing_status = AnswerSheetStatus.OCR_COMPLETED
            sheet.page_count = len(saved_results)
            sheet.processing_completed_at = datetime.now(timezone.utc)
            sheet.processed_at = datetime.now(timezone.utc)
            sheet.updated_at = datetime.now(timezone.utc)
            await self.answer_sheet_repo.save(sheet)

            # Log audit for completed OCR
            complete_log = AuditLog(
                action=AuditAction.OCR_TRIGGERED,
                resource_type="answer_sheets",
                resource_id=answer_sheet_id,
                status=AuditStatus.SUCCESS,
                user_id=user_id,
                new_values={
                    "status": AnswerSheetStatus.OCR_COMPLETED.value,
                    "page_count": sheet.page_count
                }
            )
            await self.audit_repo.save(complete_log)

            return saved_results

        except Exception as e:
            logger.error(f"OCR Pipeline failed for sheet {answer_sheet_id}: {str(e)}")
            
            # Update AnswerSheet to FAILED
            sheet.status = AnswerSheetStatus.FAILED
            sheet.processing_status = AnswerSheetStatus.FAILED
            sheet.failure_reason = str(e)
            sheet.updated_at = datetime.now(timezone.utc)
            await self.answer_sheet_repo.save(sheet)

            # Log audit for OCR failure
            fail_log = AuditLog(
                action=AuditAction.OCR_TRIGGERED,
                resource_type="answer_sheets",
                resource_id=answer_sheet_id,
                status=AuditStatus.FAILURE,
                user_id=user_id,
                error_message=str(e)
            )
            await self.audit_repo.save(fail_log)
            raise e
