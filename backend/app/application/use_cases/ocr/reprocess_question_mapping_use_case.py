"""
application/use_cases/ocr/reprocess_question_mapping_use_case.py — Reprocess Question Mapping Use Case
"""

from __future__ import annotations

import uuid

from app.domain.entities.question_mapping import QuestionMapping
from app.application.use_cases.ocr.process_question_mapping_use_case import ProcessQuestionMappingUseCase
from app.domain.repositories.question_mapping_repository import QuestionMappingRepository


class ReprocessQuestionMappingUseCase:
    """
    Clears existing mappings and re-runs the Question Detection and Mapping pipeline.
    """

    def __init__(
        self,
        question_mapping_repo: QuestionMappingRepository,
        process_use_case: ProcessQuestionMappingUseCase
    ):
        self.question_mapping_repo = question_mapping_repo
        self.process_use_case = process_use_case

    async def execute(self, answer_sheet_id: uuid.UUID, user_id: uuid.UUID | None = None) -> list[QuestionMapping]:
        """
        Deletes old mappings and re-runs the pipeline.
        """
        # 1. Clear old mappings
        await self.question_mapping_repo.delete_by_answer_sheet_id(answer_sheet_id)

        # 2. Run mapping pipeline
        return await self.process_use_case.execute(answer_sheet_id, user_id=user_id)
