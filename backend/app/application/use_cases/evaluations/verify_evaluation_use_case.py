"""
application/use_cases/evaluations/verify_evaluation_use_case.py — Verify Evaluation Use Case
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from app.domain.entities.evaluation import Evaluation
from app.domain.entities.evaluation_revision import EvaluationRevision
from app.domain.entities.audit_log import AuditLog

from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.domain.repositories.evaluation_revision_repository import EvaluationRevisionRepository
from app.domain.repositories.criterion_evaluation_repository import CriterionEvaluationRepository
from app.domain.repositories.rubric_repository import RubricRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository

from app.domain.services.rubric_scoring_service import RubricScoringService
from app.core.constants import AnswerSheetStatus, AuditAction, AuditStatus
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.application.services.final_result_synchronization_service import FinalResultSynchronizationService

logger = logging.getLogger(__name__)


class VerifyEvaluationUseCase:
    """
    Handles teacher overrides, comments, and marks verification for an AI score.
    Tracks revisions and updates answer sheet status if all questions are verified.
    """

    def __init__(
        self,
        evaluation_repo: EvaluationRepository,
        revision_repo: EvaluationRevisionRepository,
        criterion_eval_repo: CriterionEvaluationRepository,
        rubric_repo: RubricRepository,
        answer_sheet_repo: AnswerSheetRepository,
        audit_repo: AuditLogRepository,
        sync_service: FinalResultSynchronizationService | None = None
    ) -> None:
        self.evaluation_repo = evaluation_repo
        self.revision_repo = revision_repo
        self.criterion_eval_repo = criterion_eval_repo
        self.rubric_repo = rubric_repo
        self.answer_sheet_repo = answer_sheet_repo
        self.audit_repo = audit_repo
        self.sync_service = sync_service

    async def execute(
        self,
        evaluation_id: uuid.UUID,
        teacher_score: float,
        teacher_feedback: str | None,
        verifier_id: uuid.UUID,
        reason: str,
        criterion_overrides: list[dict] | None = None
    ) -> Evaluation:
        """
        Submits teacher verification and updates scores, preserving revision history.
        """
        now = datetime.now(timezone.utc)

        # 1. Fetch evaluation
        evaluation = await self.evaluation_repo.get_by_id(evaluation_id)
        if not evaluation:
            raise EntityNotFoundException(entity_type="Evaluation", entity_id=evaluation_id)

        # 2. Record revision of the previous state
        next_rev = await self.revision_repo.get_next_revision_number(evaluation.id)
        revision = EvaluationRevision(
            id=uuid.uuid4(),
            evaluation_id=evaluation.id,
            revision_number=next_rev,
            previous_score=evaluation.final_score,
            new_score=teacher_score,
            previous_feedback=evaluation.teacher_feedback or evaluation.ai_feedback,
            new_feedback=teacher_feedback,
            reason=reason,
            changed_by=verifier_id,
            created_at=now,
            updated_at=now
        )
        await self.revision_repo.save(revision)

        # 3. Update criterion-level overrides if rubric exists
        has_rubric = evaluation.rubric_id is not None
        if has_rubric and criterion_overrides:
            rubric = await self.rubric_repo.get_by_id(evaluation.rubric_id)
            if rubric:
                # Update individual criteria evaluations
                for override in criterion_overrides:
                    crit_id = override["rubric_criterion_id"]
                    c_score = override["teacher_score"]
                    c_feedback = override.get("teacher_feedback")
                    
                    ce_eval = await self.criterion_eval_repo.get_by_criterion_id(evaluation.id, crit_id)
                    if ce_eval:
                        ce_eval.teacher_score = c_score
                        ce_eval.teacher_feedback = c_feedback
                        ce_eval.is_verified = True
                        ce_eval.updated_at = now
                        await self.criterion_eval_repo.save(ce_eval)

                # Re-aggregate total score using verified criterion evaluations
                updated_ce_evals = await self.criterion_eval_repo.get_by_evaluation_id(evaluation.id)
                teacher_score = RubricScoringService.aggregate_criterion_scores(
                    criterion_evaluations=updated_ce_evals,
                    rubric=rubric,
                    question_max_marks=evaluation.max_marks
                )

        # 4. Set main evaluation scores
        evaluation.teacher_score = teacher_score
        evaluation.teacher_feedback = teacher_feedback
        evaluation.is_verified = True
        evaluation.verified_by = verifier_id
        evaluation.verified_at = now
        evaluation.updated_at = now
        
        saved_evaluation = await self.evaluation_repo.save(evaluation)

        # 5. Log Audits
        # Log score override if it differed from AI score
        if evaluation.ai_score != teacher_score:
            override_audit = AuditLog(
                action=AuditAction.SCORE_OVERRIDDEN,
                resource_type="evaluations",
                resource_id=evaluation.id,
                status=AuditStatus.SUCCESS,
                user_id=verifier_id,
                new_values={
                    "original_ai_score": evaluation.ai_score,
                    "new_teacher_score": teacher_score,
                    "reason": reason
                }
            )
            await self.audit_repo.save(override_audit)

        # Log verification submit audit
        verify_audit = AuditLog(
            action=AuditAction.VERIFICATION_SUBMITTED,
            resource_type="evaluations",
            resource_id=evaluation.id,
            status=AuditStatus.SUCCESS,
            user_id=verifier_id,
            new_values={"is_verified": True, "final_score": teacher_score}
        )
        await self.audit_repo.save(verify_audit)

        # 6. Check if all evaluations for the same answer sheet have been verified
        sheet = await self.answer_sheet_repo.get_by_id(evaluation.answer_sheet_id)
        if sheet:
            all_evals = await self.evaluation_repo.get_by_answer_sheet_id(evaluation.answer_sheet_id)
            # Find matching question mappings to make sure we evaluated all questions
            from app.infrastructure.persistence.repositories import SqlQuestionMappingRepository
            # Check if all evaluations are verified
            if all_evals and all(ev.is_verified for ev in all_evals):
                # Ensure sheet moves to VERIFIED state
                sheet.status = AnswerSheetStatus.VERIFIED
                sheet.processing_status = AnswerSheetStatus.VERIFIED
                sheet.updated_at = now
                await self.answer_sheet_repo.save(sheet)
                
                # Audit log for status change
                sheet_verified_log = AuditLog(
                    action=AuditAction.ANSWER_SHEET_STATUS_CHANGED,
                    resource_type="answer_sheets",
                    resource_id=sheet.id,
                    status=AuditStatus.SUCCESS,
                    user_id=verifier_id,
                    new_values={"status": AnswerSheetStatus.VERIFIED}
                )
                await self.audit_repo.save(sheet_verified_log)

                # Sync scores immediately
                if self.sync_service:
                    await self.sync_service.sync(sheet.id)

        return saved_evaluation
