"""
application/use_cases/ocr/process_question_mapping_use_case.py — Process Question Mapping Use Case
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
import uuid

from app.domain.entities.question_mapping import QuestionMapping
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.ocr_result_repository import OCRResultRepository
from app.domain.repositories.question_mapping_repository import QuestionMappingRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.services.question_detector_interface import QuestionDetector
from app.domain.services.answer_segmenter_interface import AnswerSegmenter
from app.domain.services.question_mapper_interface import QuestionMapper

from app.core.constants import AuditAction, AuditStatus, AnswerSheetStatus
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException

logger = logging.getLogger(__name__)


class ProcessQuestionMappingUseCase:
    """
    Coordinates the Question Detection, Answer Segmentation, and Question Mapping execution.
    Creates QuestionMapping entities and persists them to the database.
    """

    def __init__(
        self,
        answer_sheet_repo: AnswerSheetRepository,
        ocr_result_repo: OCRResultRepository,
        question_mapping_repo: QuestionMappingRepository,
        audit_repo: AuditLogRepository,
        detector: QuestionDetector,
        segmenter: AnswerSegmenter,
        mapper: QuestionMapper
    ):
        self.answer_sheet_repo = answer_sheet_repo
        self.ocr_result_repo = ocr_result_repo
        self.question_mapping_repo = question_mapping_repo
        self.audit_repo = audit_repo
        self.detector = detector
        self.segmenter = segmenter
        self.mapper = mapper

    async def execute(
        self,
        answer_sheet_id: uuid.UUID,
        user_id: uuid.UUID | None = None
    ) -> list[QuestionMapping]:
        """
        Runs the full Question Mapping pipeline.
        """
        now = datetime.now(timezone.utc)
        user_id = user_id or uuid.UUID("00000000-0000-0000-0000-000000000000")

        # 1. Load Answer Sheet
        sheet = await self.answer_sheet_repo.get_by_id(answer_sheet_id)
        if not sheet:
            raise EntityNotFoundException(entity_type="AnswerSheet", entity_id=answer_sheet_id)

        # 2. Check if OCR Results exist
        ocr_results = await self.ocr_result_repo.list_by_answer_sheet_id(answer_sheet_id)
        if not ocr_results:
            sheet.processing_status = AnswerSheetStatus.FAILED
            sheet.updated_at = now
            await self.answer_sheet_repo.save(sheet)

            # Log audit log
            fail_log = AuditLog(
                action=AuditAction.ANSWER_SHEET_STATUS_CHANGED,
                resource_type="answer_sheets",
                resource_id=answer_sheet_id,
                status=AuditStatus.FAILURE,
                user_id=user_id,
                error_message="Question mapping failed: OCR results are missing."
            )
            await self.audit_repo.save(fail_log)
            raise BusinessRuleViolationException(rule="OCR results are missing. Complete OCR before mapping.")

        try:
            # 3. Transition: QUESTION_DETECTION
            sheet.processing_status = AnswerSheetStatus.QUESTION_DETECTION
            sheet.updated_at = now
            await self.answer_sheet_repo.save(sheet)

            # Detect markers
            markers = await self.detector.detect_questions(sheet.exam_id, ocr_results)

            # 4. Transition: ANSWER_SEGMENTATION
            sheet.processing_status = AnswerSheetStatus.ANSWER_SEGMENTATION
            sheet.updated_at = now
            await self.answer_sheet_repo.save(sheet)

            # Segment answers
            segments = await self.segmenter.segment_answers(answer_sheet_id, markers, ocr_results)

            # 5. Transition: QUESTION_MAPPING
            sheet.processing_status = AnswerSheetStatus.QUESTION_MAPPING
            sheet.updated_at = now
            await self.answer_sheet_repo.save(sheet)

            # Map questions
            mappings_data = await self.mapper.map_segmented_answers_to_questions(sheet.exam_id, segments, ocr_results)

            # 6. Delete old mapping records
            await self.question_mapping_repo.delete_by_answer_sheet_id(answer_sheet_id)

            # 7. Save Mappings
            saved_mappings = []
            for data in mappings_data:
                mapping = QuestionMapping(
                    id=uuid.uuid4(),
                    answer_sheet_id=answer_sheet_id,
                    question_id=data["question_id"],
                    detected_question_number=data["detected_question_number"],
                    detected_question_label=data["detected_question_label"],
                    extracted_answer_text=data["extracted_answer_text"],
                    start_page=data["start_page"],
                    end_page=data["end_page"],
                    mapping_confidence=data["mapping_confidence"],
                    status=data["status"],
                    duplicate_question_flag=data["duplicate_question_flag"],
                    duplicate_group_id=data["duplicate_group_id"],
                    source_ocr_result_ids=data["source_ocr_result_ids"],
                    source_bounding_boxes=data["source_bounding_boxes"],
                    source_page_numbers=data["source_page_numbers"],
                    answer_word_count=data["answer_word_count"],
                    answer_character_count=data["answer_character_count"],
                    answer_page_count=data["answer_page_count"],
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                saved = await self.question_mapping_repo.save(mapping)
                saved_mappings.append(saved)

            # 8. Complete: MAPPING_COMPLETED
            sheet.processing_status = AnswerSheetStatus.MAPPING_COMPLETED
            sheet.updated_at = datetime.now(timezone.utc)
            await self.answer_sheet_repo.save(sheet)

            # Log audit log
            complete_log = AuditLog(
                action=AuditAction.ANSWER_SHEET_STATUS_CHANGED,
                resource_type="answer_sheets",
                resource_id=answer_sheet_id,
                status=AuditStatus.SUCCESS,
                user_id=user_id,
                new_values={"processing_status": "MAPPING_COMPLETED"}
            )
            await self.audit_repo.save(complete_log)

            return saved_mappings

        except Exception as e:
            logger.error(f"Question mapping pipeline failed for sheet {answer_sheet_id}: {str(e)}")
            
            sheet.processing_status = AnswerSheetStatus.FAILED
            sheet.updated_at = datetime.now(timezone.utc)
            await self.answer_sheet_repo.save(sheet)

            # Log audit log
            fail_log = AuditLog(
                action=AuditAction.ANSWER_SHEET_STATUS_CHANGED,
                resource_type="answer_sheets",
                resource_id=answer_sheet_id,
                status=AuditStatus.FAILURE,
                user_id=user_id,
                error_message=str(e)
            )
            await self.audit_repo.save(fail_log)
            raise e
