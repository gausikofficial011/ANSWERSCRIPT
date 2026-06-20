"""
application/use_cases/ocr/reprocess_ocr_use_case.py — Reprocess OCR Use Case
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import uuid

from app.domain.entities.answer_sheet import AnswerSheet
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.ocr_result_repository import OCRResultRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.core.constants import AnswerSheetStatus, AuditAction, AuditStatus
from app.domain.exceptions.domain_exception import EntityNotFoundException


class ReprocessOCRUseCase:
    """
    Use case to manually trigger reprocessing of an answer sheet's OCR.
    """

    def __init__(
        self,
        answer_sheet_repo: AnswerSheetRepository,
        ocr_result_repo: OCRResultRepository,
        audit_repo: AuditLogRepository,
        upload_dir: str = "uploads"
    ):
        self.answer_sheet_repo = answer_sheet_repo
        self.ocr_result_repo = ocr_result_repo
        self.audit_repo = audit_repo
        self.upload_dir = Path(upload_dir)

    async def execute(self, answer_sheet_id: uuid.UUID, user_id: uuid.UUID | None = None) -> AnswerSheet:
        """
        Resets and schedules reprocessing of the answer sheet's OCR.

        Args:
            answer_sheet_id: UUID of the AnswerSheet.
            user_id: UUID of the user triggering.
        """
        user_id = user_id or uuid.UUID("00000000-0000-0000-0000-000000000000")

        # 1. Fetch sheet
        sheet = await self.answer_sheet_repo.get_by_id(answer_sheet_id)
        if not sheet:
            raise EntityNotFoundException(entity_type="AnswerSheet", entity_id=answer_sheet_id)

        now = datetime.now(timezone.utc)

        # 2. Reset status to QUEUED_FOR_OCR
        sheet.status = AnswerSheetStatus.QUEUED_FOR_OCR
        sheet.processing_status = AnswerSheetStatus.QUEUED_FOR_OCR
        sheet.queued_at = now
        sheet.processing_started_at = None
        sheet.processing_completed_at = None
        sheet.failure_reason = None
        sheet.updated_at = now
        await self.answer_sheet_repo.save(sheet)

        # 3. Clean up DB records
        await self.ocr_result_repo.delete_by_answer_sheet_id(answer_sheet_id)

        # 4. Clean up disk image files (both original and processed folders)
        orig_dir = self.upload_dir / "original_images" / str(answer_sheet_id)
        proc_dir = self.upload_dir / "processed_images" / str(answer_sheet_id)
        if orig_dir.exists():
            shutil.rmtree(orig_dir, ignore_errors=True)
        if proc_dir.exists():
            shutil.rmtree(proc_dir, ignore_errors=True)

        # 5. Log audit trail
        audit_log = AuditLog(
            action=AuditAction.OCR_TRIGGERED,
            resource_type="answer_sheets",
            resource_id=answer_sheet_id,
            status=AuditStatus.SUCCESS,
            user_id=user_id,
            new_values={"status": AnswerSheetStatus.QUEUED_FOR_OCR.value}
        )
        await self.audit_repo.save(audit_log)

        # 6. Re-dispatch Celery worker task
        from app.tasks.ocr_tasks import process_answer_sheet_ocr
        process_answer_sheet_ocr.delay(str(answer_sheet_id), force_reprocess=True)

        return sheet
