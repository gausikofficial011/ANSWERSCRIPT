"""
infrastructure/persistence/repositories/sql_student_repository.py — Concrete Student SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.domain.entities.student import Student
from app.domain.repositories.student_repository import StudentRepository
from app.infrastructure.persistence.models.student_model import StudentModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository
from app.core.pagination import PaginationParams



class SqlStudentRepository(SqlBaseRepository[Student, StudentModel], StudentRepository):
    """
    SQLAlchemy implementation for Student entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, StudentModel)

    def to_entity(self, model: StudentModel) -> Student:
        return Student(
            id=model.id,
            student_number=model.student_number,
            full_name=model.full_name,
            email=model.email,
            class_section=model.class_section,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: Student) -> StudentModel:
        return StudentModel(
            id=entity.id,
            student_number=entity.student_number,
            full_name=entity.full_name,
            email=entity.email,
            class_section=entity.class_section,
            deleted_at=entity.deleted_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_student_number(self, student_number: str) -> Student | None:
        query = select(self.model_class).where(
            self.model_class.student_number == student_number,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def get_by_email(self, email: str) -> Student | None:
        query = select(self.model_class).where(
            func.lower(self.model_class.email) == email.lower(),
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def soft_delete(self, student_id: UUID) -> bool:
        stmt = (
            update(self.model_class)
            .where(self.model_class.id == student_id, self.model_class.deleted_at.is_(None))
            .values(deleted_at=func.now(), updated_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def list_students(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        class_section: str | None = None
    ) -> PaginatedResponse[Student]:
        from app.core.pagination import PaginatedResponse
        
        # Count query
        count_query = select(func.count()).select_from(self.model_class).where(self.model_class.deleted_at.is_(None))
        if class_section is not None:
            count_query = count_query.where(self.model_class.class_section == class_section)
        if search:
            search_pattern = f"%{search.strip()}%"
            count_query = count_query.where(
                (self.model_class.full_name.ilike(search_pattern)) | 
                (self.model_class.student_number.ilike(search_pattern)) |
                (self.model_class.email.ilike(search_pattern))
            )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Data query
        offset = (pagination.page - 1) * pagination.limit
        query = select(self.model_class).where(self.model_class.deleted_at.is_(None))
        if class_section is not None:
            query = query.where(self.model_class.class_section == class_section)
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.where(
                (self.model_class.full_name.ilike(search_pattern)) | 
                (self.model_class.student_number.ilike(search_pattern)) |
                (self.model_class.email.ilike(search_pattern))
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

