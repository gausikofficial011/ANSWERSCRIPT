"""
application/use_cases/plagiarism/review_plagiarism_use_case.py — Review Plagiarism Use Case
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.plagiarism_repository import PlagiarismRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository

from app.core.constants import (
    AnswerSheetStatus,
    PlagiarismStatus,
    AuditAction,
    AuditStatus
)
from app.domain.exceptions.domain_exception import (
    EntityNotFoundException,
    BusinessRuleViolationException
)

logger = logging.getLogger(__name__)


class ReviewPlagiarismUseCase:
    """
    Handles a teacher's review and decision (CONFIRMED_PLAGIARISM, FALSE_POSITIVE, DISMISSED)
    on a plagiarism report. Enforces workflow rules and logs audits.
    """

    def __init__(
        self,
        plagiarism_repo: PlagiarismRepository,
        answer_sheet_repo: AnswerSheetRepository,
        audit_repo: AuditLogRepository
    ) -> None:
        self.plagiarism_repo = plagiarism_repo
        self.answer_sheet_repo = answer_sheet_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        report_id: uuid.UUID,
        status: str,
        teacher_notes: str | None,
        user_id: uuid.UUID
    ) -> dict:
        """
        Processes teacher review for a plagiarism report.
        """
        try:
            logger.info(f"OPERATIONAL_LOG: Attempting to review plagiarism report. Report={report_id}, Status={status}, Reviewer={user_id}")
        except Exception:
            pass

        try:
            now = datetime.now(timezone.utc)

            # 1. Fetch report
            report = await self.plagiarism_repo.get_by_id(report_id)
            if not report:
                raise EntityNotFoundException(entity_type="PlagiarismReport", entity_id=report_id)

            # 2. Validate action status
            valid_statuses = {
                PlagiarismStatus.CONFIRMED_PLAGIARISM.value,
                PlagiarismStatus.FALSE_POSITIVE.value,
                PlagiarismStatus.DISMISSED.value
            }
            if status not in valid_statuses:
                raise BusinessRuleViolationException(
                    rule=f"Invalid review status. Must be one of {valid_statuses}."
                )

            old_status = report.status

            # 3. Update report details
            report.status = PlagiarismStatus(status)
            report.teacher_notes = teacher_notes
            report.reviewed_by = user_id
            report.reviewed_at = now
            report.updated_at = now
            await self.plagiarism_repo.save(report)

            # 4. Audit Log: Determine audit action
            if status == PlagiarismStatus.CONFIRMED_PLAGIARISM.value:
                audit_action = AuditAction.PLAGIARISM_CONFIRMED
            else:
                audit_action = AuditAction.PLAGIARISM_DISMISSED

            audit = AuditLog(
                action=audit_action,
                resource_type="plagiarism_reports",
                resource_id=report.id,
                status=AuditStatus.SUCCESS,
                user_id=user_id,
                old_values={"status": old_status.value if hasattr(old_status, "value") else str(old_status)},
                new_values={
                    "status": status,
                    "teacher_notes": teacher_notes
                }
            )
            await self.audit_repo.save(audit)

            # 5. Answer Sheet Status Recovery
            # If report is dismissed or marked false positive, check if we should reset plagiarism flags
            if status in {PlagiarismStatus.FALSE_POSITIVE.value, PlagiarismStatus.DISMISSED.value}:
                for sheet_id in [report.source_answer_sheet_id, report.target_answer_sheet_id]:
                    sheet = await self.answer_sheet_repo.get_by_id(sheet_id)
                    if not sheet:
                        continue

                    # Check if there are any OTHER active high risk plagiarism reports for this sheet
                    all_reports = await self.plagiarism_repo.get_sheet_similarity_reports(sheet_id)
                    active_reports = [
                        r for r in all_reports
                        if r.id != report.id
                        and r.risk_level == "HIGH_RISK"
                        and r.status not in {PlagiarismStatus.FALSE_POSITIVE, PlagiarismStatus.DISMISSED}
                    ]

                    # If no other active high-risk plagiarism report exists, restore status
                    if not active_reports:
                        sheet.plagiarism_flagged = False
                        if sheet.status == AnswerSheetStatus.PLAGIARISM_REVIEW_PENDING:
                            sheet.status = AnswerSheetStatus.EVALUATION_COMPLETED
                        await self.answer_sheet_repo.save(sheet)

                        # Log sheet status recovery audit
                        sheet_audit = AuditLog(
                            action=AuditAction.ANSWER_SHEET_STATUS_CHANGED,
                            resource_type="answer_sheets",
                            resource_id=sheet.id,
                            status=AuditStatus.SUCCESS,
                            user_id=user_id,
                            new_values={"status": sheet.status.value, "plagiarism_flagged": False}
                        )
                        await self.audit_repo.save(sheet_audit)

            try:
                logger.info(f"OPERATIONAL_LOG: Successfully reviewed plagiarism report. Report={report_id}, Status={status}, Reviewer={user_id}")
            except Exception:
                pass

            return {
                "report_id": str(report_id),
                "status": status,
                "reviewed_by": str(user_id),
                "reviewed_at": report.reviewed_at.isoformat()
            }
        except Exception as e:
            try:
                logger.error(f"OPERATIONAL_LOG: Failed to review plagiarism report. Report={report_id}, Status={status}, Reviewer={user_id}, Error={str(e)}")
            except Exception:
                pass
            raise
