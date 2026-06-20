"""
application/use_cases/evaluations/evaluate_answer_sheet_use_case.py — Evaluate Answer Sheet Use Case
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.question_mapping_repository import QuestionMappingRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.application.use_cases.evaluations.evaluate_answer_use_case import EvaluateAnswerUseCase

from app.core.constants import AnswerSheetStatus, AuditAction, AuditStatus
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException

logger = logging.getLogger(__name__)


class EvaluateAnswerSheetUseCase:
    """
    Coordinates batch AI evaluation for all mapped answers of a student answer sheet.
    """

    def __init__(
        self,
        answer_sheet_repo: AnswerSheetRepository,
        question_mapping_repo: QuestionMappingRepository,
        audit_repo: AuditLogRepository,
        evaluate_answer_use_case: EvaluateAnswerUseCase
    ) -> None:
        self.answer_sheet_repo = answer_sheet_repo
        self.question_mapping_repo = question_mapping_repo
        self.audit_repo = audit_repo
        self.evaluate_answer_use_case = evaluate_answer_use_case

    async def execute(
        self,
        answer_sheet_id: uuid.UUID,
        user_id: uuid.UUID | None = None
    ) -> dict:
        """
        Runs the batch evaluation pipeline for an answer sheet.
        """
        now = datetime.now(timezone.utc)
        user_id = user_id or uuid.UUID("00000000-0000-0000-0000-000000000000")

        # 1. Fetch answer sheet
        sheet = await self.answer_sheet_repo.get_by_id(answer_sheet_id)
        if not sheet:
            raise EntityNotFoundException(entity_type="AnswerSheet", entity_id=answer_sheet_id)

        # 2. Fetch question mappings
        mappings = await self.question_mapping_repo.list_by_answer_sheet_id(answer_sheet_id)
        if not mappings:
            raise BusinessRuleViolationException(rule="No question mappings found. Run question mapping before evaluation.")

        # 3. Set status to EVALUATION_PROCESSING
        sheet.status = AnswerSheetStatus.EVALUATION_PROCESSING
        sheet.processing_status = AnswerSheetStatus.EVALUATION_PROCESSING
        sheet.processing_started_at = now
        sheet.updated_at = now
        await self.answer_sheet_repo.save(sheet)

        # Log status audit
        status_log = AuditLog(
            action=AuditAction.ANSWER_SHEET_STATUS_CHANGED,
            resource_type="answer_sheets",
            resource_id=answer_sheet_id,
            status=AuditStatus.SUCCESS,
            user_id=user_id,
            new_values={"status": AnswerSheetStatus.EVALUATION_PROCESSING}
        )
        await self.audit_repo.save(status_log)

        requires_review = False
        evaluations_run = 0

        try:
            # 4. Evaluate each mapped question
            for mapping in mappings:
                # If question mapping status is DUPLICATE_DETECTED, we flag review required
                # and skip or still run? It's better to flag requires_review as True
                if mapping.status == "DUPLICATE_DETECTED" or mapping.duplicate_question_flag:
                    requires_review = True

                # If question_id is None, it was not mapped. Skip or flag review
                if mapping.question_id is None:
                    requires_review = True
                    continue

                # Run evaluation
                eval_record = await self.evaluate_answer_use_case.execute(
                    answer_sheet_id=answer_sheet_id,
                    question_mapping_id=mapping.id,
                    user_id=user_id
                )
                
                # Check confidence score
                if eval_record.evaluation_confidence is not None and eval_record.evaluation_confidence < 0.50:
                    requires_review = True
                
                evaluations_run += 1

            # 5. Determine final sheet status
            # If any low confidence evaluation, status becomes TEACHER_REVIEW_PENDING
            # Otherwise, EVALUATION_COMPLETED
            final_status = AnswerSheetStatus.TEACHER_REVIEW_PENDING if requires_review else AnswerSheetStatus.EVALUATION_COMPLETED
            
            sheet.status = final_status
            sheet.processing_status = AnswerSheetStatus.EVALUATION_COMPLETED
            sheet.processing_completed_at = datetime.now(timezone.utc)
            sheet.updated_at = datetime.now(timezone.utc)
            await self.answer_sheet_repo.save(sheet)

            # Log completion audit
            completion_log = AuditLog(
                action=AuditAction.ANSWER_SHEET_STATUS_CHANGED,
                resource_type="answer_sheets",
                resource_id=answer_sheet_id,
                status=AuditStatus.SUCCESS,
                user_id=user_id,
                new_values={"status": final_status}
            )
            await self.audit_repo.save(completion_log)

            return {
                "answer_sheet_id": str(answer_sheet_id),
                "total_questions": len(mappings),
                "evaluated_questions": evaluations_run,
                "requires_review": requires_review,
                "status": final_status
            }

        except Exception as e:
            logger.error(f"AI evaluation failed for answer sheet {answer_sheet_id}: {str(e)}")
            
            sheet.status = AnswerSheetStatus.FAILED
            sheet.processing_status = AnswerSheetStatus.FAILED
            sheet.failure_reason = str(e)
            sheet.updated_at = datetime.now(timezone.utc)
            await self.answer_sheet_repo.save(sheet)

            # Log status failure audit
            fail_log = AuditLog(
                action=AuditAction.ANSWER_SHEET_STATUS_CHANGED,
                resource_type="answer_sheets",
                resource_id=answer_sheet_id,
                status=AuditStatus.FAILURE,
                user_id=user_id,
                error_message=str(e),
                new_values={"status": AnswerSheetStatus.FAILED}
            )
            await self.audit_repo.save(fail_log)
            
            raise e
