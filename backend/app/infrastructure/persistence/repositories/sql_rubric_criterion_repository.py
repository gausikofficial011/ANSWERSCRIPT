"""
infrastructure/persistence/repositories/sql_rubric_criterion_repository.py — Concrete RubricCriterion SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.rubric_criterion import RubricCriterion
from app.domain.repositories.rubric_criterion_repository import RubricCriterionRepository
from app.infrastructure.persistence.models.rubric_criterion_model import RubricCriterionModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlRubricCriterionRepository(SqlBaseRepository[RubricCriterion, RubricCriterionModel], RubricCriterionRepository):
    """
    SQLAlchemy implementation for RubricCriterion entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, RubricCriterionModel)

    def to_entity(self, model: RubricCriterionModel) -> RubricCriterion:
        return RubricCriterion(
            id=model.id,
            rubric_id=model.rubric_id,
            criterion_name=model.criterion_name,
            weight=model.weight,
            max_marks=model.max_marks,
            order_index=model.order_index,
            created_at=model.created_at,
            updated_at=model.updated_at,
            criterion_description=model.criterion_description,
            expected_keywords=model.expected_keywords or []
        )

    def to_model(self, entity: RubricCriterion) -> RubricCriterionModel:
        return RubricCriterionModel(
            id=entity.id,
            rubric_id=entity.rubric_id,
            criterion_name=entity.criterion_name,
            criterion_description=entity.criterion_description,
            weight=entity.weight,
            max_marks=entity.max_marks,
            expected_keywords=entity.expected_keywords,
            order_index=entity.order_index,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_rubric_id(self, rubric_id: UUID) -> list[RubricCriterion]:
        query = (
            select(self.model_class)
            .where(self.model_class.rubric_id == rubric_id)
            .order_by(self.model_class.order_index.asc())
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def save_batch(self, criteria: list[RubricCriterion]) -> list[RubricCriterion]:
        saved_entities = []
        for c in criteria:
            saved = await self.save(c)
            saved_entities.append(saved)
        return saved_entities
