"""
infrastructure/persistence/repositories/sql_exam_repository.py — Concrete Exam SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from app.domain.entities.exam import Exam
from app.domain.repositories.exam_repository import ExamRepository
from app.infrastructure.persistence.models.exam_model import ExamModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository
from app.core.pagination import PaginationParams



class SqlExamRepository(SqlBaseRepository[Exam, ExamModel], ExamRepository):
    """
    SQLAlchemy implementation for Exam entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, ExamModel)

    def to_entity(self, model: ExamModel) -> Exam:
        return Exam(
            id=model.id,
            subject_id=model.subject_id,
            title=model.title,
            description=model.description,
            exam_date=model.exam_date,
            total_marks=model.total_marks,
            passing_marks=model.passing_marks,
            duration_minutes=model.duration_minutes,
            status=model.status,
            scoring_config=model.scoring_config or {},
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: Exam) -> ExamModel:
        return ExamModel(
            id=entity.id,
            subject_id=entity.subject_id,
            title=entity.title,
            description=entity.description,
            exam_date=entity.exam_date,
            total_marks=entity.total_marks,
            passing_marks=entity.passing_marks,
            duration_minutes=entity.duration_minutes,
            status=entity.status,
            scoring_config=entity.scoring_config,
            created_by=entity.created_by,
            deleted_at=entity.deleted_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_subject_id(self, subject_id: UUID) -> list[Exam]:
        query = select(self.model_class).where(
            self.model_class.subject_id == subject_id,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def get_by_status(self, status: str) -> list[Exam]:
        query = select(self.model_class).where(
            self.model_class.status == status,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def soft_delete(self, exam_id: UUID) -> bool:
        stmt = (
            update(self.model_class)
            .where(self.model_class.id == exam_id, self.model_class.deleted_at.is_(None))
            .values(deleted_at=func.now(), updated_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def list_exams(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        subject_id: UUID | None = None,
        status: str | None = None
    ) -> PaginatedResponse[Exam]:
        from app.core.pagination import PaginatedResponse
        
        # Count query
        count_query = select(func.count()).select_from(self.model_class).where(self.model_class.deleted_at.is_(None))
        if subject_id is not None:
            count_query = count_query.where(self.model_class.subject_id == subject_id)
        if status is not None:
            count_query = count_query.where(self.model_class.status == status)
        if search:
            search_pattern = f"%{search.strip()}%"
            count_query = count_query.where(
                self.model_class.title.ilike(search_pattern) |
                self.model_class.description.ilike(search_pattern)
            )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Data query
        offset = (pagination.page - 1) * pagination.limit
        query = select(self.model_class).where(self.model_class.deleted_at.is_(None))
        if subject_id is not None:
            query = query.where(self.model_class.subject_id == subject_id)
        if status is not None:
            query = query.where(self.model_class.status == status)
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.where(
                self.model_class.title.ilike(search_pattern) |
                self.model_class.description.ilike(search_pattern)
            )
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

