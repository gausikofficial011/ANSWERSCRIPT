"""
infrastructure/persistence/repositories/sql_final_result_repository.py — Concrete FinalResult SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from app.domain.entities.final_result import FinalResult
from app.domain.repositories.final_result_repository import FinalResultRepository
from app.infrastructure.persistence.models.final_result_model import FinalResultModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlFinalResultRepository(SqlBaseRepository[FinalResult, FinalResultModel], FinalResultRepository):
    """
    SQLAlchemy implementation for FinalResult entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, FinalResultModel)

    def to_entity(self, model: FinalResultModel) -> FinalResult:
        return FinalResult(
            id=model.id,
            answer_sheet_id=model.answer_sheet_id,
            student_id=model.student_id,
            exam_id=model.exam_id,
            total_marks_obtained=model.total_marks_obtained,
            total_marks_possible=model.total_marks_possible,
            percentage=model.percentage,
            grade=model.grade,
            pass_fail_status=model.pass_fail_status,
            is_published=model.is_published,
            published_at=model.published_at,
            published_by=model.published_by,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: FinalResult) -> FinalResultModel:
        return FinalResultModel(
            id=entity.id,
            answer_sheet_id=entity.answer_sheet_id,
            student_id=entity.student_id,
            exam_id=entity.exam_id,
            total_marks_obtained=entity.total_marks_obtained,
            total_marks_possible=entity.total_marks_possible,
            percentage=entity.percentage,
            grade=entity.grade,
            pass_fail_status=entity.pass_fail_status,
            is_published=entity.is_published,
            published_at=entity.published_at,
            published_by=entity.published_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_answer_sheet_id(self, answer_sheet_id: UUID) -> FinalResult | None:
        query = select(self.model_class).where(self.model_class.answer_sheet_id == answer_sheet_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def get_by_exam_id(self, exam_id: UUID) -> list[FinalResult]:
        query = select(self.model_class).where(self.model_class.exam_id == exam_id)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def get_student_exam_result(self, student_id: UUID, exam_id: UUID) -> FinalResult | None:
        query = select(self.model_class).where(
            self.model_class.student_id == student_id,
            self.model_class.exam_id == exam_id
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def publish_exam_results(self, exam_id: UUID, publisher_id: UUID) -> int:
        stmt = (
            update(self.model_class)
            .where(self.model_class.exam_id == exam_id, self.model_class.is_published.is_(False))
            .values(
                is_published=True,
                published_at=func.now(),
                published_by=publisher_id,
                updated_at=func.now()
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount
