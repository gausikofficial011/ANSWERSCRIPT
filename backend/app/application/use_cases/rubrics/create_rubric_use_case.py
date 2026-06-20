"""
application/use_cases/rubrics/create_rubric_use_case.py — Create Rubric Use Case
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from app.domain.entities.rubric import Rubric
from app.domain.entities.rubric_criterion import RubricCriterion
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.rubric_repository import RubricRepository
from app.domain.repositories.rubric_criterion_repository import RubricCriterionRepository
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException
from app.core.constants import GradingMode, AuditAction, AuditStatus


class CreateRubricUseCase:
    def __init__(
        self,
        rubric_repo: RubricRepository,
        criterion_repo: RubricCriterionRepository,
        question_repo: QuestionRepository,
        audit_repo: AuditLogRepository
    ):
        self.rubric_repo = rubric_repo
        self.criterion_repo = criterion_repo
        self.question_repo = question_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        question_id: uuid.UUID,
        title: str,
        total_weight: float,
        grading_mode: GradingMode,
        criteria_data: list[dict],
        created_by: uuid.UUID,
        description: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> Rubric:
        # Validate question exists
        question = await self.question_repo.get_by_id(question_id)
        if question is None:
            raise EntityNotFoundException(entity_type="Question", entity_id=question_id)

        # Validate criteria sum
        if not criteria_data:
            raise BusinessRuleViolationException(rule="Criteria list cannot be empty.")
            
        sum_weights = sum(c["weight"] for c in criteria_data)
        if abs(sum_weights - total_weight) > 1e-9:
            raise BusinessRuleViolationException(
                rule=f"Sum of criteria weights ({sum_weights}) must equal rubric total_weight ({total_weight})."
            )

        # Deactivate existing rubrics for this question
        await self.rubric_repo.deactivate_all_for_question(question_id)

        # Save Rubric Aggregate Root
        now = datetime.now(timezone.utc)
        rubric = Rubric(
            id=uuid.uuid4(),
            question_id=question_id,
            title=title.strip(),
            description=description.strip() if description else None,
            total_weight=total_weight,
            version=1,
            is_active=True,
            grading_mode=grading_mode,
            is_locked=False,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            criteria=[]
        )

        saved_rubric = await self.rubric_repo.save(rubric)

        # Save Child RubricCriteria
        criteria_entities = []
        for i, c_data in enumerate(criteria_data):
            criterion = RubricCriterion.create(
                rubric_id=saved_rubric.id,
                criterion_name=c_data["criterion_name"],
                weight=c_data["weight"],
                max_marks=c_data["max_marks"],
                order_index=c_data.get("order_index", i),
                criterion_description=c_data.get("criterion_description"),
                expected_keywords=c_data.get("expected_keywords", [])
            )
            criteria_entities.append(criterion)

        saved_criteria = await self.criterion_repo.save_batch(criteria_entities)
        saved_rubric.criteria = saved_criteria

        # Log audit
        success_log = AuditLog(
            action=AuditAction.RUBRIC_CREATED,
            resource_type="rubrics",
            resource_id=saved_rubric.id,
            status=AuditStatus.SUCCESS,
            user_id=created_by,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await self.audit_repo.save(success_log)

        return saved_rubric
