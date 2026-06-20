"""
infrastructure/persistence/repositories/sql_role_repository.py — Concrete Role SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.role import Role
from app.domain.repositories.role_repository import RoleRepository
from app.infrastructure.persistence.models.role_model import RoleModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlRoleRepository(SqlBaseRepository[Role, RoleModel], RoleRepository):
    """
    SQLAlchemy implementation for Role entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, RoleModel)

    def to_entity(self, model: RoleModel) -> Role:
        return Role(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: Role) -> RoleModel:
        return RoleModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_name(self, name: str) -> Role | None:
        query = select(self.model_class).where(self.model_class.name == name)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)
