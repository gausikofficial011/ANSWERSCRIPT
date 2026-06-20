"""
infrastructure/persistence/repositories/sql_model_answer_repository.py — Concrete ModelAnswer SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.domain.entities.model_answer import ModelAnswer
from app.domain.repositories.model_answer_repository import ModelAnswerRepository
from app.infrastructure.persistence.models.model_answer_model import ModelAnswerModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository
from app.core.pagination import PaginationParams



class SqlModelAnswerRepository(SqlBaseRepository[ModelAnswer, ModelAnswerModel], ModelAnswerRepository):
    """
    SQLAlchemy implementation for ModelAnswer entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, ModelAnswerModel)

    def to_entity(self, model: ModelAnswerModel) -> ModelAnswer:
        return ModelAnswer(
            id=model.id,
            question_id=model.question_id,
            answer_text=model.answer_text,
            keywords=model.keywords or [],
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: ModelAnswer) -> ModelAnswerModel:
        return ModelAnswerModel(
            id=entity.id,
            question_id=entity.question_id,
            answer_text=entity.answer_text,
            keywords=entity.keywords,
            created_by=entity.created_by,
            deleted_at=entity.deleted_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_question_id(self, question_id: UUID) -> ModelAnswer | None:
        query = select(self.model_class).where(
            self.model_class.question_id == question_id,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def list_model_answers(
        self,
        pagination: PaginationParams,
        question_id: UUID | None = None
    ) -> PaginatedResponse[ModelAnswer]:
        from app.core.pagination import PaginatedResponse
        
        # Count query
        count_query = select(func.count()).select_from(self.model_class).where(self.model_class.deleted_at.is_(None))
        if question_id is not None:
            count_query = count_query.where(self.model_class.question_id == question_id)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Data query
        offset = (pagination.page - 1) * pagination.limit
        query = select(self.model_class).where(self.model_class.deleted_at.is_(None))
        if question_id is not None:
            query = query.where(self.model_class.question_id == question_id)
        query = query.offset(offset).limit(pagination.limit)
        result = await self.session.execute(query)
        models = result.scalars().all()

        entities = [self.to_entity(m) for m in models]
        return PaginatedResponse(
            items=entities,
            total=total,
            page=pagination.page,
            limit=pagination.limit
        )

