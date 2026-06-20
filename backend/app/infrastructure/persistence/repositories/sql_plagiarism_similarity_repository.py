"""
infrastructure/persistence/repositories/sql_plagiarism_similarity_repository.py — Concrete PlagiarismSimilarity SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_

from app.domain.entities.plagiarism_similarity import PlagiarismSimilarity
from app.domain.repositories.plagiarism_similarity_repository import PlagiarismSimilarityRepository
from app.infrastructure.persistence.models.plagiarism_similarity_model import PlagiarismSimilarityModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlPlagiarismSimilarityRepository(
    SqlBaseRepository[PlagiarismSimilarity, PlagiarismSimilarityModel],
    PlagiarismSimilarityRepository
):
    """
    SQLAlchemy implementation for PlagiarismSimilarity entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, PlagiarismSimilarityModel)

    def to_entity(self, model: PlagiarismSimilarityModel) -> PlagiarismSimilarity:
        return PlagiarismSimilarity(
            id=model.id,
            source_answer_sheet_id=model.source_answer_sheet_id,
            target_answer_sheet_id=model.target_answer_sheet_id,
            source_question_mapping_id=model.source_question_mapping_id,
            target_question_mapping_id=model.target_question_mapping_id,
            semantic_similarity=model.semantic_similarity,
            lexical_similarity=model.lexical_similarity,
            overlap_similarity=model.overlap_similarity,
            final_similarity=model.final_similarity,
            risk_level=model.risk_level,
            created_at=model.created_at
        )

    def to_model(self, entity: PlagiarismSimilarity) -> PlagiarismSimilarityModel:
        return PlagiarismSimilarityModel(
            id=entity.id,
            source_answer_sheet_id=entity.source_answer_sheet_id,
            target_answer_sheet_id=entity.target_answer_sheet_id,
            source_question_mapping_id=entity.source_question_mapping_id,
            target_question_mapping_id=entity.target_question_mapping_id,
            semantic_similarity=entity.semantic_similarity,
            lexical_similarity=entity.lexical_similarity,
            overlap_similarity=entity.overlap_similarity,
            final_similarity=entity.final_similarity,
            risk_level=entity.risk_level,
            created_at=entity.created_at
        )

    async def list_by_answer_sheet(self, answer_sheet_id: UUID) -> list[PlagiarismSimilarity]:
        query = select(self.model_class).where(
            or_(
                self.model_class.source_answer_sheet_id == answer_sheet_id,
                self.model_class.target_answer_sheet_id == answer_sheet_id
            )
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def list_by_question_mapping(self, question_mapping_id: UUID) -> list[PlagiarismSimilarity]:
        query = select(self.model_class).where(
            or_(
                self.model_class.source_question_mapping_id == question_mapping_id,
                self.model_class.target_question_mapping_id == question_mapping_id
            )
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def list_by_pair(self, source_answer_sheet_id: UUID, target_answer_sheet_id: UUID) -> list[PlagiarismSimilarity]:
        query = select(self.model_class).where(
            or_(
                (self.model_class.source_answer_sheet_id == source_answer_sheet_id) &
                (self.model_class.target_answer_sheet_id == target_answer_sheet_id),
                (self.model_class.source_answer_sheet_id == target_answer_sheet_id) &
                (self.model_class.target_answer_sheet_id == source_answer_sheet_id)
            )
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def delete_by_answer_sheet_id(self, answer_sheet_id: UUID) -> bool:
        stmt = delete(self.model_class).where(
            or_(
                self.model_class.source_answer_sheet_id == answer_sheet_id,
                self.model_class.target_answer_sheet_id == answer_sheet_id
            )
        )
        result = await self.session.execute(stmt)
        return True
