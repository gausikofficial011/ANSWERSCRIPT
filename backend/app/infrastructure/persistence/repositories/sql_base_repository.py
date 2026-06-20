"""
infrastructure/persistence/repositories/sql_base_repository.py — Concrete Base SQL Repository

Provides generic async CRUD implementations using SQLAlchemy 2.0.
Decouples domain repositories from persistence details.
"""

from __future__ import annotations

from typing import Generic, TypeVar, Type, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.domain.repositories.base_repository import BaseRepository
from app.core.pagination import PaginatedResponse, PaginationParams

T_Entity = TypeVar("T_Entity")  # Domain Entity Type
T_Model = TypeVar("T_Model")    # SQLAlchemy ORM Model Type


class SqlBaseRepository(BaseRepository[T_Entity], Generic[T_Entity, T_Model]):
    """
    Generic SQL repository implementation using SQLAlchemy 2.0.
    """

    def __init__(self, session: AsyncSession, model_class: Type[T_Model]):
        self.session = session
        self.model_class = model_class

    def to_entity(self, model: T_Model) -> T_Entity:
        """Map ORM model instance to Domain entity instance."""
        raise NotImplementedError("to_entity must be implemented by subclasses.")

    def to_model(self, entity: T_Entity) -> T_Model:
        """Map Domain entity instance to ORM model instance."""
        raise NotImplementedError("to_model must be implemented by subclasses.")

    async def get_by_id(self, entity_id: UUID) -> T_Entity | None:
        if hasattr(self.model_class, "deleted_at"):
            query = select(self.model_class).where(
                self.model_class.id == entity_id,
                self.model_class.deleted_at.is_(None)
            )
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()
        else:
            model = await self.session.get(self.model_class, entity_id)
            
        if model is None:
            return None
        return self.to_entity(model)

    async def get_all(self, pagination: PaginationParams) -> PaginatedResponse[T_Entity]:
        # Count total records
        count_query = select(func.count()).select_from(self.model_class)
        if hasattr(self.model_class, "deleted_at"):
            count_query = count_query.where(self.model_class.deleted_at.is_(None))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Query paginated records
        offset = (pagination.page - 1) * pagination.limit
        query = select(self.model_class).offset(offset).limit(pagination.limit)
        if hasattr(self.model_class, "deleted_at"):
            query = query.where(self.model_class.deleted_at.is_(None))
        result = await self.session.execute(query)
        models = result.scalars().all()

        entities = [self.to_entity(m) for m in models]
        return PaginatedResponse(
            items=entities,
            total=total,
            page=pagination.page,
            limit=pagination.limit
        )

    async def save(self, entity: T_Entity) -> T_Entity:
        entity_id = getattr(entity, "id")
        existing_model = await self.session.get(self.model_class, entity_id)

        model = self.to_model(entity)

        if existing_model is not None:
            await self.session.merge(model)
        else:
            self.session.add(model)

        await self.session.flush()
        
        # Reload latest state
        if hasattr(self.model_class, "deleted_at"):
            query = select(self.model_class).where(
                self.model_class.id == entity_id,
                self.model_class.deleted_at.is_(None)
            )
            result = await self.session.execute(query)
            refreshed_model = result.scalar_one_or_none()
        else:
            refreshed_model = await self.session.get(self.model_class, entity_id)
            
        if refreshed_model is None:
            # If soft deleted in database, return the saved entity as is
            return entity
        return self.to_entity(refreshed_model)

    async def delete(self, entity_id: UUID) -> bool:
        model = await self.session.get(self.model_class, entity_id)
        if model is None:
            return False
            
        if hasattr(self.model_class, "deleted_at"):
            # If the model supports soft delete, verify it's not already soft deleted
            if model.deleted_at is not None:
                return False
            model.deleted_at = func.now()
            if hasattr(model, "is_active"):
                model.is_active = False
        else:
            await self.session.delete(model)
            
        await self.session.flush()
        return True

    async def exists(self, entity_id: UUID) -> bool:
        query = select(func.count()).select_from(self.model_class).where(getattr(self.model_class, "id") == entity_id)
        if hasattr(self.model_class, "deleted_at"):
            query = query.where(self.model_class.deleted_at.is_(None))
        result = await self.session.execute(query)
        return result.scalar_one() > 0
