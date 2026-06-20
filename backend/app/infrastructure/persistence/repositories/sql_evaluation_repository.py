"""
infrastructure/persistence/repositories/sql_evaluation_repository.py — Concrete Evaluation SQL Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.evaluation import Evaluation
from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.infrastructure.persistence.models.evaluation_model import EvaluationModel
from app.infrastructure.persistence.repositories.sql_base_repository import SqlBaseRepository


class SqlEvaluationRepository(SqlBaseRepository[Evaluation, EvaluationModel], EvaluationRepository):
    """
    SQLAlchemy implementation for Evaluation entity persistence.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, EvaluationModel)

    def to_entity(self, model: EvaluationModel) -> Evaluation:
        return Evaluation(
            id=model.id,
            answer_sheet_id=model.answer_sheet_id,
            question_mapping_id=model.question_mapping_id,
            question_id=model.question_id,
            model_answer_id=model.model_answer_id,
            max_marks=model.max_marks,
            rubric_id=model.rubric_id,
            ai_score=model.ai_score,
            similarity_score=model.similarity_score,
            keyword_match_score=model.keyword_match_score,
            ai_feedback=model.ai_feedback,
            teacher_score=model.teacher_score,
            teacher_feedback=model.teacher_feedback,
            is_verified=model.is_verified,
            verified_by=model.verified_by,
            verified_at=model.verified_at,
            evaluation_model=model.evaluation_model,
            evaluation_confidence=model.evaluation_confidence,
            explanation=model.explanation,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def to_model(self, entity: Evaluation) -> EvaluationModel:
        return EvaluationModel(
            id=entity.id,
            answer_sheet_id=entity.answer_sheet_id,
            question_mapping_id=entity.question_mapping_id,
            question_id=entity.question_id,
            model_answer_id=entity.model_answer_id,
            max_marks=entity.max_marks,
            rubric_id=entity.rubric_id,
            ai_score=entity.ai_score,
            similarity_score=entity.similarity_score,
            keyword_match_score=entity.keyword_match_score,
            ai_feedback=entity.ai_feedback,
            teacher_score=entity.teacher_score,
            teacher_feedback=entity.teacher_feedback,
            final_score=entity.final_score,
            is_verified=entity.is_verified,
            verified_by=entity.verified_by,
            verified_at=entity.verified_at,
            evaluation_model=entity.evaluation_model,
            evaluation_confidence=entity.evaluation_confidence,
            explanation=entity.explanation,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_answer_sheet_id(self, answer_sheet_id: UUID) -> list[Evaluation]:
        query = select(self.model_class).where(self.model_class.answer_sheet_id == answer_sheet_id)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]

    async def get_by_question_id(self, answer_sheet_id: UUID, question_id: UUID) -> Evaluation | None:
        query = select(self.model_class).where(
            self.model_class.answer_sheet_id == answer_sheet_id,
            self.model_class.question_id == question_id
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.to_entity(model)

    async def save_batch(self, evaluations: list[Evaluation]) -> list[Evaluation]:
        saved_entities = []
        for e in evaluations:
            saved = await self.save(e)
            saved_entities.append(saved)
        return saved_entities

    async def get_pending_verifications(self, exam_id: UUID | None = None) -> list[Evaluation]:
        # Evaluated but not verified
        query = select(self.model_class).where(self.model_class.is_verified.is_(False))
        if exam_id is not None:
            # Need to join answer_sheets to filter by exam_id
            from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
            query = query.join(AnswerSheetModel).where(AnswerSheetModel.exam_id == exam_id)
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.to_entity(m) for m in models]
