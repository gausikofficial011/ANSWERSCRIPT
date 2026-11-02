"""
infrastructure/persistence/repositories/sql_criterion_evaluation_repository.py — Concrete CriterionEvaluation SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.criterion_evaluation import CriterionEvaluation
from app.domain.repositories.criterion_evaluation_repository import CriterionEvaluationRepository
from app.infrastructure.persistence.models.criterion_evaluation_model import CriterionEvaluationModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlCriterionEvaluationRepository(SqlBaseRepository[CriterionEvaluation, CriterionEvaluationModel], CriterionEvaluationRepository):
    """
    SQLAlchemy implementation for CriterionEvaluation entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, CriterionEvaluationModel)

    def to_entity(self, model: CriterionEvaluationModel) -> CriterionEvaluation:
        return CriterionEvaluation(
            id=model.id,
            evaluation_id=model.evaluation_id,
            rubric_criterion_id=model.rubric_criterion_id,
            ai_score=model.ai_score,
            ai_semantic_score=model.ai_semantic_score,
            ai_keyword_score=model.ai_keyword_score,
            ai_feedback=model.ai_feedback,
            teacher_score=model.teacher_score,
            teacher_feedback=model.teacher_feedback,
            is_verified=model.is_verified,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: CriterionEvaluation) -> CriterionEvaluationModel:
        return CriterionEvaluationModel(
            id=entity.id,
            evaluation_id=entity.evaluation_id,
            rubric_criterion_id=entity.rubric_criterion_id,
            ai_score=entity.ai_score,
            ai_semantic_score=entity.ai_semantic_score,
            ai_keyword_score=entity.ai_keyword_score,
            ai_feedback=entity.ai_feedback,
            teacher_score=entity.teacher_score,
            teacher_feedback=entity.teacher_feedback,
            final_score=entity.final_score,
            is_verified=entity.is_verified,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_evaluation_id(self, evaluation_id: UUID) -> list[CriterionEvaluation]:
        query = select(self.model_class).where(self.model_class.evaluation_id == evaluation_id)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def get_by_criterion_id(self, evaluation_id: UUID, rubric_criterion_id: UUID) -> CriterionEvaluation | None:
        query = select(self.model_class).where(
            self.model_class.evaluation_id == evaluation_id,
            self.model_class.rubric_criterion_id == rubric_criterion_id
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def save_batch(self, criterion_evaluations: list[CriterionEvaluation]) -> list[CriterionEvaluation]:
        saved_entities = []
        for ce in criterion_evaluations:
            saved = await self.save(ce)
            saved_entities.append(saved)
        return saved_entities
