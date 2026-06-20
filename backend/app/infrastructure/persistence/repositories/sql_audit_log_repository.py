"""
infrastructure/persistence/repositories/sql_audit_log_repository.py — Concrete AuditLog SQL Repository
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.persistence.models.audit_log_model import AuditLogModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository
from app.core.pagination import PaginatedResponse, PaginationParams


class SqlAuditLogRepository(SqlBaseRepository[AuditLog, AuditLogModel], AuditLogRepository):
    """
    SQLAlchemy implementation for AuditLog entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditLogModel)

    def to_entity(self, model: AuditLogModel) -> AuditLog:
        return AuditLog(
            id=model.id,
            user_id=model.user_id,
            action=model.action,
            resource_type=model.resource_type,
            resource_id=model.resource_id,
            old_values=model.old_values,
            new_values=model.new_values,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            status=model.status,
            error_message=model.error_message,
            created_at=model.created_at
        )

    def to_model(self, entity: AuditLog) -> AuditLogModel:
        return AuditLogModel(
            id=entity.id,
            user_id=entity.user_id,
            action=entity.action,
            resource_type=entity.resource_type,
            resource_id=entity.resource_id,
            old_values=entity.old_values,
            new_values=entity.new_values,
            ip_address=entity.ip_address,
            user_agent=entity.user_agent,
            status=entity.status,
            error_message=entity.error_message,
            created_at=entity.created_at
        )

    async def filter_logs(
        self,
        user_id: UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: UUID | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        pagination: PaginationParams = PaginationParams(),
    ) -> PaginatedResponse[AuditLog]:
        count_query = select(func.count()).select_from(self.model_class)
        query = select(self.model_class)

        # Apply filters
        for q in [count_query, query]:
            if user_id is not None:
                q = q.where(self.model_class.user_id == user_id)
            if action is not None:
                q = q.where(self.model_class.action == action)
            if resource_type is not None:
                q = q.where(self.model_class.resource_type == resource_type)
            if resource_id is not None:
                q = q.where(self.model_class.resource_id == resource_id)
            if status is not None:
                q = q.where(self.model_class.status == status)
            if start_date is not None:
                q = q.where(self.model_class.created_at >= start_date)
            if end_date is not None:
                q = q.where(self.model_class.created_at <= end_date)

        # Execute count
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Apply pagination & order to details query
        offset = (pagination.page - 1) * pagination.limit
        query = query.order_by(self.model_class.created_at.desc()).offset(offset).limit(pagination.limit)
        
        result = await self.session.execute(query)
        models = result.scalars().all()

        entities = [self.to_entity(m) for m in models]
        return PaginatedResponse(
            items=entities,
            total=total,
            page=pagination.page,
            limit=pagination.limit
        )
