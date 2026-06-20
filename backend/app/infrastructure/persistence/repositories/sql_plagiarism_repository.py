"""
infrastructure/persistence/repositories/sql_plagiarism_repository.py — Concrete Plagiarism SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_

from app.domain.entities.plagiarism_report import PlagiarismReport
from app.domain.repositories.plagiarism_repository import PlagiarismRepository
from app.infrastructure.persistence.models.plagiarism_report_model import PlagiarismReportModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlPlagiarismRepository(SqlBaseRepository[PlagiarismReport, PlagiarismReportModel], PlagiarismRepository):
    """
    SQLAlchemy implementation for PlagiarismReport entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, PlagiarismReportModel)

    def to_entity(self, model: PlagiarismReportModel) -> PlagiarismReport:
        from app.core.constants import PlagiarismStatus
        return PlagiarismReport(
            id=model.id,
            exam_id=model.exam_id,
            source_answer_sheet_id=model.source_answer_sheet_id,
            target_answer_sheet_id=model.target_answer_sheet_id,
            similarity_percentage=model.similarity_percentage,
            highest_similarity=model.highest_similarity,
            risk_level=model.risk_level,
            similarity_details=model.similarity_details,
            flagged_questions=model.flagged_questions,
            status=PlagiarismStatus(model.status) if model.status else PlagiarismStatus.DETECTED,
            reviewed_by=model.reviewed_by,
            reviewed_at=model.reviewed_at,
            teacher_notes=model.teacher_notes,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: PlagiarismReport) -> PlagiarismReportModel:
        return PlagiarismReportModel(
            id=entity.id,
            exam_id=entity.exam_id,
            source_answer_sheet_id=entity.source_answer_sheet_id,
            target_answer_sheet_id=entity.target_answer_sheet_id,
            similarity_percentage=entity.similarity_percentage,
            highest_similarity=entity.highest_similarity,
            risk_level=entity.risk_level,
            similarity_details=entity.similarity_details,
            flagged_questions=entity.flagged_questions,
            status=entity.status.value if hasattr(entity.status, "value") else entity.status,
            reviewed_by=entity.reviewed_by,
            reviewed_at=entity.reviewed_at,
            teacher_notes=entity.teacher_notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_exam_id(self, exam_id: UUID) -> list[PlagiarismReport]:
        query = select(self.model_class).where(self.model_class.exam_id == exam_id)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def get_sheet_similarity_reports(self, answer_sheet_id: UUID) -> list[PlagiarismReport]:
        query = select(self.model_class).where(
            or_(
                self.model_class.source_answer_sheet_id == answer_sheet_id,
                self.model_class.target_answer_sheet_id == answer_sheet_id
            )
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def save_batch(self, reports: list[PlagiarismReport]) -> list[PlagiarismReport]:
        saved_entities = []
        for r in reports:
            saved = await self.save(r)
            saved_entities.append(saved)
        return saved_entities

    async def delete_by_exam_id(self, exam_id: UUID) -> None:
        stmt = delete(self.model_class).where(self.model_class.exam_id == exam_id)
        await self.session.execute(stmt)
