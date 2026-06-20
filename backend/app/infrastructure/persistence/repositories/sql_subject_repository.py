"""
infrastructure/persistence/repositories/sql_subject_repository.py — Concrete Subject SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.domain.entities.subject import Subject
from app.domain.repositories.subject_repository import SubjectRepository
from app.infrastructure.persistence.models.subject_model import SubjectModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository
from app.core.pagination import PaginationParams



class SqlSubjectRepository(SqlBaseRepository[Subject, SubjectModel], SubjectRepository):
    """
    SQLAlchemy implementation for Subject entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, SubjectModel)

    def to_entity(self, model: SubjectModel) -> Subject:
        return Subject(
            id=model.id,
            name=model.name,
            code=model.code,
            description=model.description,
            language=model.language,
            created_by=model.created_by,
            is_active=model.is_active,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: Subject) -> SubjectModel:
        return SubjectModel(
            id=entity.id,
            name=entity.name,
            code=entity.code,
            description=entity.description,
            language=entity.language,
            created_by=entity.created_by,
            is_active=entity.is_active,
            deleted_at=entity.deleted_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_code(self, code: str) -> Subject | None:
        query = select(self.model_class).where(
            func.lower(self.model_class.code) == code.lower(),
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def list_active_subjects(self) -> list[Subject]:
        query = select(self.model_class).where(
            self.model_class.is_active.is_(True),
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def soft_delete(self, subject_id: UUID) -> bool:
        stmt = (
            update(self.model_class)
            .where(self.model_class.id == subject_id, self.model_class.deleted_at.is_(None))
            .values(deleted_at=func.now(), is_active=False, updated_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def list_subjects(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        is_active: bool | None = None
    ) -> PaginatedResponse[Subject]:
        from app.core.pagination import PaginatedResponse
        
        # Count query
        count_query = select(func.count()).select_from(self.model_class).where(self.model_class.deleted_at.is_(None))
        if is_active is not None:
            count_query = count_query.where(self.model_class.is_active == is_active)
        if search:
            search_pattern = f"%{search.strip()}%"
            count_query = count_query.where(
                (self.model_class.name.ilike(search_pattern)) | 
                (self.model_class.code.ilike(search_pattern))
            )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Data query
        offset = (pagination.page - 1) * pagination.limit
        query = select(self.model_class).where(self.model_class.deleted_at.is_(None))
        if is_active is not None:
            query = query.where(self.model_class.is_active == is_active)
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.where(
                (self.model_class.name.ilike(search_pattern)) | 
                (self.model_class.code.ilike(search_pattern))
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

