"""
infrastructure/persistence/repositories/sql_rubric_repository.py — Concrete Rubric SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from app.domain.entities.rubric import Rubric
from app.domain.entities.rubric_criterion import RubricCriterion
from app.domain.repositories.rubric_repository import RubricRepository
from app.infrastructure.persistence.models.rubric_model import RubricModel
from app.infrastructure.persistence.models.rubric_criterion_model import RubricCriterionModel
from app.infrastructure.persistence.models.criterion_evaluation_model import CriterionEvaluationModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository
from app.core.pagination import PaginationParams



class SqlRubricRepository(SqlBaseRepository[Rubric, RubricModel], RubricRepository):
    """
    SQLAlchemy implementation for Rubric entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, RubricModel)

    def to_entity(self, model: RubricModel) -> Rubric:
        criteria = []
        if hasattr(model, "criteria") and model.criteria:
            criteria = [
                RubricCriterion(
                    id=c.id,
                    rubric_id=c.rubric_id,
                    criterion_name=c.criterion_name,
                    weight=c.weight,
                    max_marks=c.max_marks,
                    order_index=c.order_index,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                    criterion_description=c.criterion_description,
                    expected_keywords=c.expected_keywords or []
                )
                for c in model.criteria
            ]
        return Rubric(
            id=model.id,
            question_id=model.question_id,
            title=model.title,
            total_weight=model.total_weight,
            version=model.version,
            is_active=model.is_active,
            grading_mode=model.grading_mode,
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            description=model.description,
            criteria=criteria
        )

    def to_model(self, entity: Rubric) -> RubricModel:
        return RubricModel(
            id=entity.id,
            question_id=entity.question_id,
            title=entity.title,
            description=entity.description,
            total_weight=entity.total_weight,
            version=entity.version,
            is_active=entity.is_active,
            grading_mode=entity.grading_mode,
            created_by=entity.created_by,
            deleted_at=entity.deleted_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def _is_rubric_locked(self, rubric_id: UUID) -> bool:
        query = (
            select(func.count(CriterionEvaluationModel.id))
            .join(RubricCriterionModel)
            .where(RubricCriterionModel.rubric_id == rubric_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one() > 0

    async def get_by_id(self, entity_id: UUID) -> Rubric | None:
        query = (
            select(self.model_class)
            .options(selectinload(self.model_class.criteria))
            .where(
                self.model_class.id == entity_id,
                self.model_class.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        
        is_locked = await self._is_rubric_locked(model.id)
        entity = self.to_entity(model)
        entity.is_locked = is_locked
        return entity

    async def get_active_by_question_id(self, question_id: UUID) -> Rubric | None:
        query = (
            select(self.model_class)
            .options(selectinload(self.model_class.criteria))
            .where(
                self.model_class.question_id == question_id,
                self.model_class.is_active.is_(True),
                self.model_class.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        
        is_locked = await self._is_rubric_locked(model.id)
        entity = self.to_entity(model)
        entity.is_locked = is_locked
        return entity

    async def list_versions_by_question_id(self, question_id: UUID) -> list[Rubric]:
        query = (
            select(self.model_class)
            .options(selectinload(self.model_class.criteria))
            .where(
                self.model_class.question_id == question_id,
                self.model_class.deleted_at.is_(None)
            )
            .order_by(self.model_class.version.desc())
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        entities = []
        for m in models:
            is_locked = await self._is_rubric_locked(m.id)
            entity = self.to_entity(m)
            entity.is_locked = is_locked
            entities.append(entity)
        return entities

    async def deactivate_all_for_question(self, question_id: UUID) -> None:
        stmt = (
            update(self.model_class)
            .where(
                self.model_class.question_id == question_id,
                self.model_class.deleted_at.is_(None)
            )
            .values(is_active=False, updated_at=func.now())
        )
        await self.session.execute(stmt)

    async def list_rubrics(
        self,
        pagination: PaginationParams,
        question_id: UUID | None = None,
        is_active: bool | None = None
    ) -> PaginatedResponse[Rubric]:
        from app.core.pagination import PaginatedResponse
        
        # Count query
        count_query = select(func.count()).select_from(self.model_class).where(self.model_class.deleted_at.is_(None))
        if question_id is not None:
            count_query = count_query.where(self.model_class.question_id == question_id)
        if is_active is not None:
            count_query = count_query.where(self.model_class.is_active == is_active)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Data query
        offset = (pagination.page - 1) * pagination.limit
        query = (
            select(self.model_class)
            .options(selectinload(self.model_class.criteria))
            .where(self.model_class.deleted_at.is_(None))
        )
        if question_id is not None:
            query = query.where(self.model_class.question_id == question_id)
        if is_active is not None:
            query = query.where(self.model_class.is_active == is_active)
        query = query.order_by(self.model_class.version.desc()).offset(offset).limit(pagination.limit)
        result = await self.session.execute(query)
        models = result.scalars().all()

        entities = []
        for m in models:
            is_locked = await self._is_rubric_locked(m.id)
            entity = self.to_entity(m)
            entity.is_locked = is_locked
            entities.append(entity)
            
        return PaginatedResponse(
            items=entities,
            total=total,
            page=pagination.page,
            limit=pagination.limit
        )

