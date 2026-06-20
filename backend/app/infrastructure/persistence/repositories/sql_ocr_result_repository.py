"""
infrastructure/persistence/repositories/sql_ocr_result_repository.py — Concrete OCRResult SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.domain.entities.ocr_result import OCRResult
from app.domain.repositories.ocr_result_repository import OCRResultRepository
from app.infrastructure.persistence.models.ocr_result_model import OCRResultModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlOCRResultRepository(SqlBaseRepository[OCRResult, OCRResultModel], OCRResultRepository):
    """
    SQLAlchemy implementation for OCRResult entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, OCRResultModel)

    def to_entity(self, model: OCRResultModel) -> OCRResult:
        return OCRResult(
            id=model.id,
            answer_sheet_id=model.answer_sheet_id,
            page_number=model.page_number,
            extracted_text=model.extracted_text,
            bounding_boxes=model.bounding_boxes,
            low_confidence_flag=model.low_confidence_flag,
            confidence_score=model.confidence_score,
            average_confidence=model.average_confidence,
            words_detected=model.words_detected,
            processing_time=model.processing_time,
            ocr_engine_version=model.ocr_engine_version,
            preprocessing_version=model.preprocessing_version,
            original_image_path=model.original_image_path,
            processed_image_path=model.processed_image_path,
            status=model.status,
            language_detected=model.language_detected,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: OCRResult) -> OCRResultModel:
        return OCRResultModel(
            id=entity.id,
            answer_sheet_id=entity.answer_sheet_id,
            page_number=entity.page_number,
            extracted_text=entity.extracted_text,
            bounding_boxes=entity.bounding_boxes,
            low_confidence_flag=entity.low_confidence_flag,
            confidence_score=entity.confidence_score,
            average_confidence=entity.average_confidence,
            words_detected=entity.words_detected,
            processing_time=entity.processing_time,
            ocr_engine_version=entity.ocr_engine_version,
            preprocessing_version=entity.preprocessing_version,
            original_image_path=entity.original_image_path,
            processed_image_path=entity.processed_image_path,
            status=entity.status,
            language_detected=entity.language_detected,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def list_by_answer_sheet_id(self, answer_sheet_id: UUID) -> list[OCRResult]:
        query = select(self.model_class).where(self.model_class.answer_sheet_id == answer_sheet_id).order_by(self.model_class.page_number.asc())
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(model) for model in models]

    async def get_by_page(self, answer_sheet_id: UUID, page_number: int) -> OCRResult | None:
        query = select(self.model_class).where(
            self.model_class.answer_sheet_id == answer_sheet_id,
            self.model_class.page_number == page_number
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def delete_by_answer_sheet_id(self, answer_sheet_id: UUID) -> bool:
        query = delete(self.model_class).where(self.model_class.answer_sheet_id == answer_sheet_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return (result.rowcount or 0) > 0
