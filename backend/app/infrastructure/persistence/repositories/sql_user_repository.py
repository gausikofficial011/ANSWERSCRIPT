"""
infrastructure/persistence/repositories/sql_user_repository.py — Concrete User SQL Repository
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.persistence.models.user_model import UserModel
from app.infrastructure.persistence.models.role_model import RoleModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlUserRepository(SqlBaseRepository[User, UserModel], UserRepository):
    """
    SQLAlchemy implementation for User entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)

    def to_entity(self, model: UserModel) -> User:
        from sqlalchemy import inspect
        role_name = None
        try:
            insp = inspect(model)
            if "role" not in insp.unloaded and getattr(model, "role", None) is not None:
                role_name = model.role.name
        except Exception:
            pass

        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            role_id=model.role_id,
            is_active=model.is_active,
            is_verified=model.is_verified,
            last_login_at=model.last_login_at,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            role=role_name
        )

    def to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            hashed_password=entity.hashed_password,
            full_name=entity.full_name,
            role_id=entity.role_id,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
            last_login_at=entity.last_login_at,
            deleted_at=entity.deleted_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_id(self, entity_id: UUID) -> User | None:
        from sqlalchemy.orm import joinedload
        model = await self.session.get(
            self.model_class,
            entity_id,
            options=[joinedload(UserModel.role)]
        )
        if model is None:
            return None
        return self.to_entity(model)

    async def get_by_email(self, email: str) -> User | None:
        from sqlalchemy.orm import joinedload
        query = select(self.model_class).options(joinedload(UserModel.role)).where(
            func.lower(self.model_class.email) == email.lower(),
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def get_by_username(self, username: str) -> User | None:
        from sqlalchemy.orm import joinedload
        query = select(self.model_class).options(joinedload(UserModel.role)).where(
            self.model_class.username == username,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)


    async def get_active_users_by_role(self, role: str) -> list[User]:
        query = (
            select(self.model_class)
            .join(RoleModel)
            .where(
                RoleModel.name == role,
                self.model_class.is_active.is_(True),
                self.model_class.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def email_exists(self, email: str) -> bool:
        query = select(func.count()).select_from(self.model_class).where(
            func.lower(self.model_class.email) == email.lower()
        )
        result = await self.session.execute(query)
        return result.scalar_one() > 0

    async def username_exists(self, username: str) -> bool:
        query = select(func.count()).select_from(self.model_class).where(
            self.model_class.username == username
        )
        result = await self.session.execute(query)
        return result.scalar_one() > 0

    async def update_last_login(self, user_id: UUID) -> None:
        stmt = (
            update(self.model_class)
            .where(self.model_class.id == user_id)
            .values(last_login_at=func.now(), updated_at=func.now())
        )
        await self.session.execute(stmt)

    async def soft_delete(self, user_id: UUID) -> bool:
        stmt = (
            update(self.model_class)
            .where(self.model_class.id == user_id, self.model_class.deleted_at.is_(None))
            .values(deleted_at=func.now(), is_active=False, updated_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
