"""
infrastructure/persistence/repositories/sql_extracted_answer_repository.py — Concrete ExtractedAnswer SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.extracted_answer import ExtractedAnswer
from app.domain.repositories.extracted_answer_repository import ExtractedAnswerRepository
from app.infrastructure.persistence.models.extracted_answer_model import ExtractedAnswerModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlExtractedAnswerRepository(SqlBaseRepository[ExtractedAnswer, ExtractedAnswerModel], ExtractedAnswerRepository):
    """
    SQLAlchemy implementation for ExtractedAnswer entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, ExtractedAnswerModel)

    def to_entity(self, model: ExtractedAnswerModel) -> ExtractedAnswer:
        return ExtractedAnswer(
            id=model.id,
            ocr_result_id=model.ocr_result_id,
            question_id=model.question_id,
            answer_sheet_id=model.answer_sheet_id,
            extracted_text=model.extracted_text,
            detected_question_number=model.detected_question_number,
            extraction_confidence=model.extraction_confidence,
            page_number=model.page_number,
            bounding_box=model.bounding_box,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: ExtractedAnswer) -> ExtractedAnswerModel:
        return ExtractedAnswerModel(
            id=entity.id,
            ocr_result_id=entity.ocr_result_id,
            question_id=entity.question_id,
            answer_sheet_id=entity.answer_sheet_id,
            extracted_text=entity.extracted_text,
            detected_question_number=entity.detected_question_number,
            extraction_confidence=entity.extraction_confidence,
            page_number=entity.page_number,
            bounding_box=entity.bounding_box,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_answer_sheet_id(self, answer_sheet_id: UUID) -> list[ExtractedAnswer]:
        query = select(self.model_class).where(self.model_class.answer_sheet_id == answer_sheet_id)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def get_by_question_id(self, answer_sheet_id: UUID, question_id: UUID) -> ExtractedAnswer | None:
        query = select(self.model_class).where(
            self.model_class.answer_sheet_id == answer_sheet_id,
            self.model_class.question_id == question_id
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def save_batch(self, extracted_answers: list[ExtractedAnswer]) -> list[ExtractedAnswer]:
        saved_entities = []
        for ea in extracted_answers:
            saved = await self.save(ea)
            saved_entities.append(saved)
        return saved_entities
