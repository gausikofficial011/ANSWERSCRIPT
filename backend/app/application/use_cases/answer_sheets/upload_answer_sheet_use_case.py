"""
application/use_cases/answer_sheets/upload_answer_sheet_use_case.py — Upload Answer Sheet Use Case
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from app.domain.entities.answer_sheet import AnswerSheet
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.student_repository import StudentRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.services.malware_scanner import MalwareScanner
from app.domain.services.student_mapping_service import StudentMappingService
from app.storage.uploads.base_storage import BaseFileStorage
from app.infrastructure.storage.file_validator_service import FileValidatorService
from app.infrastructure.storage.file_metadata_service import FileMetadataService
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException
from app.core.constants import AnswerSheetStatus, AuditAction, AuditStatus


class UploadAnswerSheetUseCase:
    def __init__(
        self,
        answer_sheet_repo: AnswerSheetRepository,
        exam_repo: ExamRepository,
        student_repo: StudentRepository,
        audit_repo: AuditLogRepository,
        storage_service: BaseFileStorage,
        validator_service: FileValidatorService,
        metadata_service: FileMetadataService,
        scanner: MalwareScanner,
        mapping_service: StudentMappingService
    ):
        self.answer_sheet_repo = answer_sheet_repo
        self.exam_repo = exam_repo
        self.student_repo = student_repo
        self.audit_repo = audit_repo
        self.storage_service = storage_service
        self.validator_service = validator_service
        self.metadata_service = metadata_service
        self.scanner = scanner
        self.mapping_service = mapping_service

    async def execute(
        self,
        exam_id: uuid.UUID,
        filename: str,
        file_data: bytes,
        uploaded_by: uuid.UUID,
        manual_student_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> AnswerSheet:
        # 1. Validate Exam exists
        exam = await self.exam_repo.get_by_id(exam_id)
        if exam is None:
            raise EntityNotFoundException(entity_type="Exam", entity_id=exam_id)

        # 2. File Format and Limit Validation
        mime_type = self.validator_service.validate(filename, file_data)

        # 3. Malware Check
        is_clean = await self.scanner.scan(file_data, filename)
        if not is_clean:
            fail_log = AuditLog(
                action=AuditAction.ANSWER_SHEET_UPLOADED,
                resource_type="answer_sheets",
                status=AuditStatus.FAILURE,
                user_id=uploaded_by,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message=f"Malware scanning flagged file: '{filename}'"
            )
            await self.audit_repo.save(fail_log)
            raise BusinessRuleViolationException(rule="Malware scan failed. The file is flagged as unsafe.")

        # 4. Integrity and Corruption Check
        self.metadata_service.verify_integrity(file_data, filename)

        # 5. Calculate File SHA256 Hash
        file_hash = self.metadata_service.calculate_sha256(file_data)

        # 6. Check for Duplicate Files
        duplicate = await self.answer_sheet_repo.get_by_hash(file_hash)
        if duplicate:
            raise BusinessRuleViolationException(
                rule=f"This identical file has already been uploaded for this exam under ID '{duplicate.id}'."
            )

        # 7. Map Student Number
        student_id = await self.mapping_service.map_student(filename, file_data, manual_student_id)

        # 8. Check Duplicate Submissions (Supersession Invariant)
        supersedes_id = None
        previous_sheet = await self.answer_sheet_repo.get_by_student_and_exam(student_id, exam_id)
        if previous_sheet:
            supersedes_id = previous_sheet.id

        # 9. Storage Persistence
        now = datetime.now(timezone.utc)
        destination_path = f"answer_sheets/{exam_id}/{now.year}/{now.month:02d}/"
        stored_filename = f"{uuid.uuid4()}{Path(filename).suffix.lower()}"
        
        stored_file = self.storage_service.save(
            file_data=file_data,
            destination_path=destination_path,
            filename=stored_filename,
            mime_type=mime_type
        )

        page_count = self.metadata_service.extract_page_count(file_data, filename)

        # 10. Register AnswerSheet in DB
        answer_sheet = AnswerSheet(
            id=uuid.uuid4(),
            exam_id=exam_id,
            student_id=student_id,
            uploaded_by=uploaded_by,
            original_filename=filename,
            stored_filename=stored_filename,
            file_path=stored_file.relative_path,
            file_size_bytes=stored_file.size_bytes,
            mime_type=mime_type,
            file_hash=file_hash,
            page_count=page_count,
            status=AnswerSheetStatus.UPLOADED,
            supersedes_answer_sheet_id=supersedes_id,
            processing_status=AnswerSheetStatus.UPLOADED,
            created_at=now,
            updated_at=now
        )

        saved_sheet = await self.answer_sheet_repo.save(answer_sheet)

        # 11. Handle Supersession linking on previous sheet
        if previous_sheet:
            previous_sheet.status = AnswerSheetStatus.SUPERSEDED
            previous_sheet.superseded_by_answer_sheet_id = saved_sheet.id
            previous_sheet.updated_at = now
            await self.answer_sheet_repo.save(previous_sheet)

            # Log audit for replaced sheet
            replace_log = AuditLog(
                action=AuditAction.ANSWER_SHEET_REPLACED,
                resource_type="answer_sheets",
                resource_id=supersedes_id,
                status=AuditStatus.SUCCESS,
                user_id=uploaded_by,
                old_values={"status": str(AnswerSheetStatus.SUPERSEDED.value)},
                new_values={"superseded_by_answer_sheet_id": str(saved_sheet.id)},
                ip_address=ip_address,
                user_agent=user_agent
            )
            await self.audit_repo.save(replace_log)

        # 12. Audit Log Upload success
        success_log = AuditLog(
            action=AuditAction.ANSWER_SHEET_UPLOADED,
            resource_type="answer_sheets",
            resource_id=saved_sheet.id,
            status=AuditStatus.SUCCESS,
            user_id=uploaded_by,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        # 13. Queue OCR Task
        saved_sheet.status = AnswerSheetStatus.QUEUED_FOR_OCR
        saved_sheet.processing_status = AnswerSheetStatus.QUEUED_FOR_OCR
        saved_sheet.queued_at = datetime.now(timezone.utc)
        await self.answer_sheet_repo.save(saved_sheet)

        # Audit Log Queue action
        queue_log = AuditLog(
            action=AuditAction.ANSWER_SHEET_QUEUED,
            resource_type="answer_sheets",
            resource_id=saved_sheet.id,
            status=AuditStatus.SUCCESS,
            user_id=uploaded_by,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(queue_log)

        # Dispatch Celery task
        from app.tasks.ocr_tasks import process_answer_sheet_ocr
        process_answer_sheet_ocr.delay(str(saved_sheet.id))

        return saved_sheet
