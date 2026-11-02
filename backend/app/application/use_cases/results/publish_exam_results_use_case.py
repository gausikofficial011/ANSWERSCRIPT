"""
application/use_cases/results/publish_exam_results_use_case.py — Publish Exam Results Use Case
"""

from __future__ import annotations
import uuid
import logging
from datetime import datetime, timezone

from app.domain.repositories.final_result_repository import FinalResultRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository

from app.domain.entities.audit_log import AuditLog
from app.core.constants import AnswerSheetStatus, AuditAction, AuditStatus
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException

logger = logging.getLogger(__name__)


class PublishExamResultsUseCase:
    """
    Validates publishing criteria for an exam's scores list and flags them as published.
    Enforces that only fully verified sheets free of active plagiarism blocks are published.
    """

    def __init__(
        self,
        final_result_repo: FinalResultRepository,
        answer_sheet_repo: AnswerSheetRepository,
        exam_repo: ExamRepository,
        audit_repo: AuditLogRepository
    ) -> None:
        self.final_result_repo = final_result_repo
        self.answer_sheet_repo = answer_sheet_repo
        self.exam_repo = exam_repo
        self.audit_repo = audit_repo

    async def execute(self, exam_id: uuid.UUID, publisher_id: uuid.UUID) -> dict:
        """
        Executes results release workflow after validating exam eligibility.
        """
        try:
            logger.info(f"OPERATIONAL_LOG: Attempting to publish exam results. Exam={exam_id}, Publisher={publisher_id}")
        except Exception:
            pass

        try:
            now = datetime.now(timezone.utc)

            # 1. Fetch Exam
            exam = await self.exam_repo.get_by_id(exam_id)
            if not exam:
                raise EntityNotFoundException(entity_type="Exam", entity_id=exam_id)

            # 2. Fetch all answer sheets for the exam
            sheets = await self.answer_sheet_repo.get_all_by_exam_id(exam_id)
            
            # Filter out deleted and superseded sheets
            active_sheets = [
                s for s in sheets 
                if s.deleted_at is None 
                and getattr(s, "superseded_by_answer_sheet_id", None) is None
            ]

            if not active_sheets:
                raise BusinessRuleViolationException(
                    rule="Cannot publish results. No active student answer sheets found for this exam."
                )

            # 3. Validate answer sheet statuses and plagiarism blocks
            for sheet in active_sheets:
                # Check for plagiarism flags
                if getattr(sheet, "plagiarism_flagged", False):
                    raise BusinessRuleViolationException(
                        rule=(
                            f"Cannot publish results. Answer sheet {sheet.original_filename} "
                            "has unresolved or confirmed plagiarism flags."
                        )
                    )

                # Check verification status
                # Only VERIFIED or already PUBLISHED sheets are allowed.
                if sheet.status not in {AnswerSheetStatus.VERIFIED, AnswerSheetStatus.PUBLISHED}:
                    raise BusinessRuleViolationException(
                        rule=(
                            f"Cannot publish results. Answer sheet {sheet.original_filename} "
                            f"has incomplete verification (current status: {sheet.status})."
                        )
                    )

            # 4. Fetch final results to check if already published
            results = await self.final_result_repo.get_by_exam_id(exam_id)
            if results and all(r.is_published for r in results):
                raise BusinessRuleViolationException(
                    rule="Results for this exam have already been published."
                )

            # 5. Bulk update final_results database table using the repository
            published_count = await self.final_result_repo.publish_exam_results(
                exam_id=exam_id,
                publisher_id=publisher_id
            )

            # 6. Transition answer sheet statuses to PUBLISHED
            for sheet in active_sheets:
                if sheet.status != AnswerSheetStatus.PUBLISHED:
                    sheet.status = AnswerSheetStatus.PUBLISHED
                    sheet.processing_status = AnswerSheetStatus.PUBLISHED
                    sheet.updated_at = now
                    await self.answer_sheet_repo.save(sheet)

            # 7. Log Audit Log Event
            audit = AuditLog(
                action=AuditAction.RESULT_PUBLISHED,
                resource_type="exams",
                resource_id=exam_id,
                status=AuditStatus.SUCCESS,
                user_id=publisher_id,
                new_values={
                    "is_published": True,
                    "published_count": published_count,
                    "published_at": now.isoformat()
                }
            )
            await self.audit_repo.save(audit)

            try:
                logger.info(
                    f"OPERATIONAL_LOG: Successfully published exam results. Exam={exam_id}, Publisher={publisher_id}, PublishedCount={published_count}"
                )
            except Exception:
                pass

            return {
                "exam_id": str(exam_id),
                "published_count": published_count,
                "published_at": now.isoformat(),
                "published_by": str(publisher_id)
            }
        except Exception as e:
            try:
                logger.error(
                    f"OPERATIONAL_LOG: Failed to publish exam results. Exam={exam_id}, Publisher={publisher_id}, Error={str(e)}"
                )
            except Exception:
                pass
            raise
