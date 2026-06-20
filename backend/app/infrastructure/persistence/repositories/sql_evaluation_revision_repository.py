"""
infrastructure/persistence/repositories/sql_evaluation_revision_repository.py — Concrete EvaluationRevision SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.domain.entities.evaluation_revision import EvaluationRevision
from app.domain.repositories.evaluation_revision_repository import EvaluationRevisionRepository
from app.infrastructure.persistence.models.evaluation_revision_model import EvaluationRevisionModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlEvaluationRevisionRepository(SqlBaseRepository[EvaluationRevision, EvaluationRevisionModel], EvaluationRevisionRepository):
    """
    SQLAlchemy implementation for EvaluationRevision entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, EvaluationRevisionModel)

    def to_entity(self, model: EvaluationRevisionModel) -> EvaluationRevision:
        return EvaluationRevision(
            id=model.id,
            evaluation_id=model.evaluation_id,
            revision_number=model.revision_number,
            previous_score=model.previous_score,
            new_score=model.new_score,
            previous_feedback=model.previous_feedback,
            new_feedback=model.new_feedback,
            reason=model.reason,
            changed_by=model.changed_by,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: EvaluationRevision) -> EvaluationRevisionModel:
        return EvaluationRevisionModel(
            id=entity.id,
            evaluation_id=entity.evaluation_id,
            revision_number=entity.revision_number,
            previous_score=entity.previous_score,
            new_score=entity.new_score,
            previous_feedback=entity.previous_feedback,
            new_feedback=entity.new_feedback,
            reason=entity.reason,
            changed_by=entity.changed_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_evaluation_id(self, evaluation_id: UUID) -> list[EvaluationRevision]:
        query = (
            select(self.model_class)
            .where(self.model_class.evaluation_id == evaluation_id)
            .order_by(self.model_class.revision_number.asc())
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def get_next_revision_number(self, evaluation_id: UUID) -> int:
        query = select(func.max(self.model_class.revision_number)).where(
            self.model_class.evaluation_id == evaluation_id
        )
        result = await self.session.execute(query)
        max_num = result.scalar()
        return (max_num or 0) + 1
