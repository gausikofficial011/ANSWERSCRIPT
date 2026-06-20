"""
infrastructure/persistence/repositories/sql_notification_repository.py — Concrete Notification SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.domain.entities.notification import Notification
from app.domain.repositories.notification_repository import NotificationRepository
from app.infrastructure.persistence.models.notification_model import NotificationModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlNotificationRepository(SqlBaseRepository[Notification, NotificationModel], NotificationRepository):
    """
    SQLAlchemy implementation for Notification entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, NotificationModel)

    def to_entity(self, model: NotificationModel) -> Notification:
        return Notification(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            message=model.message,
            type=model.type,
            category=model.category,
            resource_type=model.resource_type,
            resource_id=model.resource_id,
            is_read=model.is_read,
            read_at=model.read_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: Notification) -> NotificationModel:
        return NotificationModel(
            id=entity.id,
            user_id=entity.user_id,
            title=entity.title,
            message=entity.message,
            type=entity.type,
            category=entity.category,
            resource_type=entity.resource_type,
            resource_id=entity.resource_id,
            is_read=entity.is_read,
            read_at=entity.read_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_user_id(self, user_id: UUID, is_read: bool | None = None) -> list[Notification]:
        query = (
            select(self.model_class)
            .where(self.model_class.user_id == user_id)
            .order_by(self.model_class.created_at.desc())
        )
        if is_read is not None:
            query = query.where(self.model_class.is_read == is_read)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def get_unread_count(self, user_id: UUID) -> int:
        query = select(func.count()).select_from(self.model_class).where(
            self.model_class.user_id == user_id,
            self.model_class.is_read.is_(False)
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def mark_as_read(self, notification_id: UUID) -> bool:
        stmt = (
            update(self.model_class)
            .where(self.model_class.id == notification_id, self.model_class.is_read.is_(False))
            .values(is_read=True, read_at=func.now(), updated_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def mark_all_as_read(self, user_id: UUID) -> int:
        stmt = (
            update(self.model_class)
            .where(self.model_class.user_id == user_id, self.model_class.is_read.is_(False))
            .values(is_read=True, read_at=func.now(), updated_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount
