"""
infrastructure/persistence/repositories/sql_question_repository.py — Concrete Question SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.domain.entities.question import Question
from app.domain.repositories.question_repository import QuestionRepository
from app.infrastructure.persistence.models.question_model import QuestionModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository
from app.core.pagination import PaginationParams



class SqlQuestionRepository(SqlBaseRepository[Question, QuestionModel], QuestionRepository):
    """
    SQLAlchemy implementation for Question entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, QuestionModel)

    def to_entity(self, model: QuestionModel) -> Question:
        return Question(
            id=model.id,
            exam_id=model.exam_id,
            question_number=model.question_number,
            question_text=model.question_text,
            marks=model.marks,
            question_type=model.question_type,
            language=model.language,
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: Question) -> QuestionModel:
        return QuestionModel(
            id=entity.id,
            exam_id=entity.exam_id,
            question_number=entity.question_number,
            question_text=entity.question_text,
            marks=entity.marks,
            question_type=entity.question_type,
            language=entity.language,
            created_by=entity.created_by,
            deleted_at=entity.deleted_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_exam_id(self, exam_id: UUID) -> list[Question]:
        query = (
            select(self.model_class)
            .where(
                self.model_class.exam_id == exam_id,
                self.model_class.deleted_at.is_(None)
            )
            .order_by(self.model_class.question_number.asc())
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def get_by_number(self, exam_id: UUID, question_number: int) -> Question | None:
        query = select(self.model_class).where(
            self.model_class.exam_id == exam_id,
            self.model_class.question_number == question_number,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def list_questions(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        exam_id: UUID | None = None
    ) -> PaginatedResponse[Question]:
        from app.core.pagination import PaginatedResponse
        
        # Count query
        count_query = select(func.count()).select_from(self.model_class).where(self.model_class.deleted_at.is_(None))
        if exam_id is not None:
            count_query = count_query.where(self.model_class.exam_id == exam_id)
        if search:
            search_pattern = f"%{search.strip()}%"
            count_query = count_query.where(
                self.model_class.question_text.ilike(search_pattern)
            )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Data query
        offset = (pagination.page - 1) * pagination.limit
        query = select(self.model_class).where(self.model_class.deleted_at.is_(None))
        if exam_id is not None:
            query = query.where(self.model_class.exam_id == exam_id)
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.where(
                self.model_class.question_text.ilike(search_pattern)
            )
        query = query.order_by(self.model_class.question_number.asc()).offset(offset).limit(pagination.limit)
        result = await self.session.execute(query)
        models = result.scalars().all()

        entities = [self.to_entity(m) for m in models]
        return PaginatedResponse(
            items=entities,
            total=total,
            page=pagination.page,
            limit=pagination.limit
        )

