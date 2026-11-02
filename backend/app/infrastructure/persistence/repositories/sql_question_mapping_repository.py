"""
infrastructure/persistence/repositories/sql_question_mapping_repository.py — Concrete QuestionMapping SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.domain.entities.question_mapping import QuestionMapping
from app.domain.repositories.question_mapping_repository import QuestionMappingRepository
from app.infrastructure.persistence.models.question_mapping_model import QuestionMappingModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlQuestionMappingRepository(SqlBaseRepository[QuestionMapping, QuestionMappingModel], QuestionMappingRepository):
    """
    SQLAlchemy implementation for QuestionMapping entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, QuestionMappingModel)

    def to_entity(self, model: QuestionMappingModel) -> QuestionMapping:
        return QuestionMapping(
            id=model.id,
            answer_sheet_id=model.answer_sheet_id,
            question_id=model.question_id,
            detected_question_number=model.detected_question_number,
            detected_question_label=model.detected_question_label,
            extracted_answer_text=model.extracted_answer_text,
            start_page=model.start_page,
            end_page=model.end_page,
            mapping_confidence=model.mapping_confidence,
            status=model.status,
            duplicate_question_flag=model.duplicate_question_flag,
            duplicate_group_id=model.duplicate_group_id,
            source_ocr_result_ids=[UUID(uid) if isinstance(uid, str) else uid for uid in model.source_ocr_result_ids],
            source_bounding_boxes=model.source_bounding_boxes,
            source_page_numbers=model.source_page_numbers,
            answer_word_count=model.answer_word_count,
            answer_character_count=model.answer_character_count,
            answer_page_count=model.answer_page_count,
            corrected_question_id=model.corrected_question_id,
            corrected_by_user_id=model.corrected_by_user_id,
            corrected_at=model.corrected_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: QuestionMapping) -> QuestionMappingModel:
        return QuestionMappingModel(
            id=entity.id,
            answer_sheet_id=entity.answer_sheet_id,
            question_id=entity.question_id,
            detected_question_number=entity.detected_question_number,
            detected_question_label=entity.detected_question_label,
            extracted_answer_text=entity.extracted_answer_text,
            start_page=entity.start_page,
            end_page=entity.end_page,
            mapping_confidence=entity.mapping_confidence,
            status=entity.status,
            duplicate_question_flag=entity.duplicate_question_flag,
            duplicate_group_id=entity.duplicate_group_id,
            source_ocr_result_ids=[str(uid) for uid in entity.source_ocr_result_ids],
            source_bounding_boxes=entity.source_bounding_boxes,
            source_page_numbers=entity.source_page_numbers,
            answer_word_count=entity.answer_word_count,
            answer_character_count=entity.answer_character_count,
            answer_page_count=entity.answer_page_count,
            corrected_question_id=entity.corrected_question_id,
            corrected_by_user_id=entity.corrected_by_user_id,
            corrected_at=entity.corrected_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def list_by_answer_sheet_id(self, answer_sheet_id: UUID) -> list[QuestionMapping]:
        query = select(self.model_class).where(self.model_class.answer_sheet_id == answer_sheet_id).order_by(
            self.model_class.detected_question_number.asc().nullslast()
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(model) for model in models]

    async def delete_by_answer_sheet_id(self, answer_sheet_id: UUID) -> bool:
        query = delete(self.model_class).where(self.model_class.answer_sheet_id == answer_sheet_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return (result.rowcount or 0) > 0
