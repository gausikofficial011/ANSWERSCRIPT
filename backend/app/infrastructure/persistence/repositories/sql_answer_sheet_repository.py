"""
infrastructure/persistence/repositories/sql_answer_sheet_repository.py — Concrete AnswerSheet SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.domain.entities.answer_sheet import AnswerSheet
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository
from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.constants import AnswerSheetStatus


class SqlAnswerSheetRepository(SqlBaseRepository[AnswerSheet, AnswerSheetModel], AnswerSheetRepository):
    """
    SQLAlchemy implementation for AnswerSheet entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, AnswerSheetModel)

    def to_entity(self, model: AnswerSheetModel) -> AnswerSheet:
        return AnswerSheet(
            id=model.id,
            exam_id=model.exam_id,
            student_id=model.student_id,
            uploaded_by=model.uploaded_by,
            original_filename=model.original_filename,
            stored_filename=model.stored_filename,
            file_path=model.file_path,
            file_size_bytes=model.file_size_bytes,
            mime_type=model.mime_type,
            file_hash=model.file_hash,
            page_count=model.page_count,
            status=model.status,
            error_message=model.error_message,
            processed_at=model.processed_at,
            deleted_at=model.deleted_at,
            supersedes_answer_sheet_id=model.supersedes_answer_sheet_id,
            superseded_by_answer_sheet_id=model.superseded_by_answer_sheet_id,
            processing_status=AnswerSheetStatus(model.processing_status) if model.processing_status else AnswerSheetStatus.UPLOADED,
            queued_at=model.queued_at,
            processing_started_at=model.processing_started_at,
            processing_completed_at=model.processing_completed_at,
            failure_reason=model.failure_reason,
            plagiarism_flagged=model.plagiarism_flagged,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: AnswerSheet) -> AnswerSheetModel:
        return AnswerSheetModel(
            id=entity.id,
            exam_id=entity.exam_id,
            student_id=entity.student_id,
            uploaded_by=entity.uploaded_by,
            original_filename=entity.original_filename,
            stored_filename=entity.stored_filename,
            file_path=entity.file_path,
            file_size_bytes=entity.file_size_bytes,
            mime_type=entity.mime_type,
            file_hash=entity.file_hash,
            page_count=entity.page_count,
            status=entity.status,
            error_message=entity.error_message,
            processed_at=entity.processed_at,
            deleted_at=entity.deleted_at,
            supersedes_answer_sheet_id=entity.supersedes_answer_sheet_id,
            superseded_by_answer_sheet_id=entity.superseded_by_answer_sheet_id,
            processing_status=entity.processing_status.value if entity.processing_status else AnswerSheetStatus.UPLOADED.value,
            queued_at=entity.queued_at,
            processing_started_at=entity.processing_started_at,
            processing_completed_at=entity.processing_completed_at,
            failure_reason=entity.failure_reason,
            plagiarism_flagged=entity.plagiarism_flagged,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_exam(
        self,
        exam_id: UUID,
        pagination: PaginationParams,
        status: str | None = None,
    ) -> PaginatedResponse[AnswerSheet]:
        count_query = select(func.count()).select_from(self.model_class).where(
            self.model_class.exam_id == exam_id,
            self.model_class.deleted_at.is_(None)
        )
        if status:
            count_query = count_query.where(self.model_class.status == status)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        offset = (pagination.page - 1) * pagination.limit
        query = select(self.model_class).where(
            self.model_class.exam_id == exam_id,
            self.model_class.deleted_at.is_(None)
        ).offset(offset).limit(pagination.limit)
        if status:
            query = query.where(self.model_class.status == status)
        result = await self.session.execute(query)
        models = result.scalars().all()

        entities = [self.to_entity(m) for m in models]
        return PaginatedResponse(
            items=entities,
            total=total,
            page=pagination.page,
            limit=pagination.limit
        )

    async def get_by_student_and_exam(self, student_id: UUID, exam_id: UUID) -> AnswerSheet | None:
        query = select(self.model_class).where(
            self.model_class.student_id == student_id,
            self.model_class.exam_id == exam_id,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def get_by_status(self, status: str, limit: int = 50) -> list[AnswerSheet]:
        query = select(self.model_class).where(
            self.model_class.status == status,
            self.model_class.deleted_at.is_(None)
        ).limit(limit)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def update_status(
        self,
        answer_sheet_id: UUID,
        status: str,
        error_message: str | None = None,
    ) -> AnswerSheet | None:
        values = {"status": status, "updated_at": func.now()}
        if error_message is not None:
            values["error_message"] = error_message
        if status in (AnswerSheetStatus.VERIFIED.value, AnswerSheetStatus.FAILED.value, "OCR_COMPLETED", "EVALUATION_COMPLETED"):
            values["processed_at"] = func.now()

        stmt = (
            update(self.model_class)
            .where(self.model_class.id == answer_sheet_id)
            .values(**values)
        )
        await self.session.execute(stmt)
        
        # Load the updated sheet
        return await self.get_by_id(answer_sheet_id)

    async def get_by_stored_filename(self, stored_filename: str) -> AnswerSheet | None:
        query = select(self.model_class).where(
            self.model_class.stored_filename == stored_filename,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def get_by_hash(self, file_hash: str) -> AnswerSheet | None:
        query = select(self.model_class).where(
            self.model_class.file_hash == file_hash,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def count_by_exam_and_status(self, exam_id: UUID, status: str) -> int:
        query = select(func.count()).select_from(self.model_class).where(
            self.model_class.exam_id == exam_id,
            self.model_class.status == status,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def list_answer_sheets(
        self,
        pagination: PaginationParams,
        exam_id: UUID | None = None,
        student_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> PaginatedResponse[AnswerSheet]:
        count_query = select(func.count()).select_from(self.model_class).where(
            self.model_class.deleted_at.is_(None)
        )
        query = select(self.model_class).where(
            self.model_class.deleted_at.is_(None)
        )

        if exam_id:
            count_query = count_query.where(self.model_class.exam_id == exam_id)
            query = query.where(self.model_class.exam_id == exam_id)
        if student_id:
            count_query = count_query.where(self.model_class.student_id == student_id)
            query = query.where(self.model_class.student_id == student_id)
        if status:
            count_query = count_query.where(self.model_class.status == status)
            query = query.where(self.model_class.status == status)
        if search:
            search_pattern = f"%{search}%"
            count_query = count_query.where(self.model_class.original_filename.ilike(search_pattern))
            query = query.where(self.model_class.original_filename.ilike(search_pattern))

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        offset = (pagination.page - 1) * pagination.limit
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

    async def get_all_by_exam_id(self, exam_id: UUID) -> list[AnswerSheet]:
        query = select(self.model_class).where(
            self.model_class.exam_id == exam_id,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]
