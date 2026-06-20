"""
application/use_cases/evaluations/re_evaluate_use_case.py — Re-evaluate Use Case
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from app.domain.entities.evaluation import Evaluation
from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.application.use_cases.evaluations.evaluate_answer_use_case import EvaluateAnswerUseCase

from app.core.constants import AuditAction, AuditStatus
from app.domain.exceptions.domain_exception import EntityNotFoundException

logger = logging.getLogger(__name__)


class ReEvaluateUseCase:
    """
    Triggers re-run of AI evaluation for a specific answer record.
    """

    def __init__(
        self,
        evaluation_repo: EvaluationRepository,
        audit_repo: AuditLogRepository,
        evaluate_answer_use_case: EvaluateAnswerUseCase
    ) -> None:
        self.evaluation_repo = evaluation_repo
        self.audit_repo = audit_repo
        self.evaluate_answer_use_case = evaluate_answer_use_case

    async def execute(
        self,
        evaluation_id: uuid.UUID,
        user_id: uuid.UUID | None = None
    ) -> Evaluation:
        """
        Executes the AI scorer to calculate the scores again.
        """
        user_id = user_id or uuid.UUID("00000000-0000-0000-0000-000000000000")

        # 1. Fetch evaluation
        evaluation = await self.evaluation_repo.get_by_id(evaluation_id)
        if not evaluation:
            raise EntityNotFoundException(entity_type="Evaluation", entity_id=evaluation_id)

        # 2. Invoke EvaluateAnswerUseCase
        # evaluate_answer_use_case will load model answers, rubrics and run calculations
        updated_eval = await self.evaluate_answer_use_case.execute(
            answer_sheet_id=evaluation.answer_sheet_id,
            question_mapping_id=evaluation.question_mapping_id,
            user_id=user_id
        )

        return updated_eval
