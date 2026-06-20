"""
application/use_cases/rubrics/update_rubric_use_case.py — Update Rubric Use Case
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from app.domain.entities.rubric import Rubric
from app.domain.entities.rubric_criterion import RubricCriterion
from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.rubric_repository import RubricRepository
from app.domain.repositories.rubric_criterion_repository import RubricCriterionRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException
from app.core.constants import GradingMode, AuditAction, AuditStatus


class UpdateRubricUseCase:
    def __init__(
        self,
        rubric_repo: RubricRepository,
        criterion_repo: RubricCriterionRepository,
        audit_repo: AuditLogRepository
    ):
        self.rubric_repo = rubric_repo
        self.criterion_repo = criterion_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        rubric_id: uuid.UUID,
        updater_id: uuid.UUID,
        title: str | None = None,
        description: str | None = None,
        total_weight: float | None = None,
        grading_mode: GradingMode | None = None,
        criteria_data: list[dict] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> Rubric:
        # Load rubric (which evaluates is_locked inside SqlRubricRepository)
        rubric = await self.rubric_repo.get_by_id(rubric_id)
        if rubric is None:
            raise EntityNotFoundException(entity_type="Rubric", entity_id=rubric_id)

        # Enforce lock invariant check
        if rubric.is_locked:
            # CREATE A NEW VERSION (SUPERSADE)
            next_version = rubric.version + 1
            
            # Deactivate all active versions for this question
            await self.rubric_repo.deactivate_all_for_question(rubric.question_id)
            
            new_title = title if title is not None else rubric.title
            new_desc = description if description is not None else rubric.description
            new_weight = total_weight if total_weight is not None else rubric.total_weight
            new_mode = grading_mode if grading_mode is not None else rubric.grading_mode
            
            # Decide criteria list to associate with the new version
            raw_criteria = []
            if criteria_data is not None:
                # Validate weights
                sum_weights = sum(c["weight"] for c in criteria_data)
                if abs(sum_weights - new_weight) > 1e-9:
                    raise BusinessRuleViolationException(
                        rule=f"Sum of criteria weights ({sum_weights}) must equal rubric total_weight ({new_weight})."
                    )
                raw_criteria = criteria_data
            else:
                # Copy old criteria over
                raw_criteria = [
                    {
                        "criterion_name": c.criterion_name,
                        "criterion_description": c.criterion_description,
                        "weight": c.weight,
                        "max_marks": c.max_marks,
                        "expected_keywords": c.expected_keywords,
                        "order_index": c.order_index
                    }
                    for c in rubric.criteria
                ]
                
            # Create new Rubric version
            now = datetime.now(timezone.utc)
            new_rubric = Rubric(
                id=uuid.uuid4(),
                question_id=rubric.question_id,
                title=new_title.strip(),
                description=new_desc.strip() if new_desc else None,
                total_weight=new_weight,
                version=next_version,
                is_active=True,
                grading_mode=new_mode,
                is_locked=False,
                created_by=updater_id,
                created_at=now,
                updated_at=now,
                criteria=[]
            )
            
            saved_rubric = await self.rubric_repo.save(new_rubric)
            
            # Save child Criteria
            criteria_entities = []
            for i, c_data in enumerate(raw_criteria):
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
            
            # Log version rotation audit trail
            success_log = AuditLog(
                action=AuditAction.RUBRIC_UPDATED,
                resource_type="rubrics",
                resource_id=saved_rubric.id,
                status=AuditStatus.SUCCESS,
                user_id=updater_id,
                old_values={"superseded_rubric_id": str(rubric_id), "version": rubric.version},
                new_values={"active_rubric_id": str(saved_rubric.id), "version": saved_rubric.version},
                ip_address=ip_address,
                user_agent=user_agent
            )
            await self.audit_repo.save(success_log)
            
            return saved_rubric
            
        else:
            # DIRECT UPDATE (UNLOCKED)
            if title is not None:
                rubric.title = title.strip()
            if description is not None:
                rubric.description = description.strip() if description.strip() else None
            if total_weight is not None:
                rubric.total_weight = total_weight
            if grading_mode is not None:
                rubric.grading_mode = grading_mode
                
            rubric.updated_at = datetime.now(timezone.utc)
            
            if criteria_data is not None:
                # Validate weights
                sum_weights = sum(c["weight"] for c in criteria_data)
                if abs(sum_weights - rubric.total_weight) > 1e-9:
                    raise BusinessRuleViolationException(
                        rule=f"Sum of criteria weights ({sum_weights}) must equal rubric total_weight ({rubric.total_weight})."
                    )
                # Delete existing criteria
                for c in rubric.criteria:
                    await self.criterion_repo.delete(c.id)
                
                # Save new criteria list
                criteria_entities = []
                for i, c_data in enumerate(criteria_data):
                    criterion = RubricCriterion.create(
                        rubric_id=rubric.id,
                        criterion_name=c_data["criterion_name"],
                        weight=c_data["weight"],
                        max_marks=c_data["max_marks"],
                        order_index=c_data.get("order_index", i),
                        criterion_description=c_data.get("criterion_description"),
                        expected_keywords=c_data.get("expected_keywords", [])
                    )
                    criteria_entities.append(criterion)
                    
                saved_criteria = await self.criterion_repo.save_batch(criteria_entities)
                rubric.criteria = saved_criteria
                
            saved_rubric = await self.rubric_repo.save(rubric)
            
            # Log standard update audit trail
            success_log = AuditLog(
                action=AuditAction.RUBRIC_UPDATED,
                resource_type="rubrics",
                resource_id=rubric_id,
                status=AuditStatus.SUCCESS,
                user_id=updater_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            await self.audit_repo.save(success_log)
            
            return saved_rubric
