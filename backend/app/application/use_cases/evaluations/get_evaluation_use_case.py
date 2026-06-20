"""
application/use_cases/evaluations/get_evaluation_use_case.py — Get Evaluation Use Case
"""

from __future__ import annotations

import uuid
from typing import Any

from app.domain.entities.evaluation import Evaluation
from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.domain.repositories.evaluation_revision_repository import EvaluationRevisionRepository
from app.domain.repositories.criterion_evaluation_repository import CriterionEvaluationRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException


class GetEvaluationUseCase:
    """
    Retrieves detailed information for an evaluation including criteria breakdowns and revisions.
    """

    def __init__(
        self,
        evaluation_repo: EvaluationRepository,
        revision_repo: EvaluationRevisionRepository,
        criterion_eval_repo: CriterionEvaluationRepository
    ) -> None:
        self.evaluation_repo = evaluation_repo
        self.revision_repo = revision_repo
        self.criterion_eval_repo = criterion_eval_repo

    async def execute(self, evaluation_id: uuid.UUID) -> dict[str, Any]:
        """
        Retrieves evaluation and detailed criteria evaluations + revisions.
        """
        evaluation = await self.evaluation_repo.get_by_id(evaluation_id)
        if not evaluation:
            raise EntityNotFoundException(entity_type="Evaluation", entity_id=evaluation_id)

        criterion_evals = await self.criterion_eval_repo.get_by_evaluation_id(evaluation_id)
        revisions = await self.revision_repo.get_by_evaluation_id(evaluation_id)

        return {
            "evaluation": evaluation,
            "criteria_evaluations": criterion_evals,
            "revisions": revisions
        }
