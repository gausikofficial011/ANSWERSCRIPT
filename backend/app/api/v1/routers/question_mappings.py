"""
api/v1/routers/question_mappings.py — Question Mappings REST API Endpoints
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_teacher
from app.api.v1.schemas.question_mapping_schemas import QuestionMappingResponse, QuestionMappingSummaryResponse
from app.infrastructure.persistence.database import get_db_session

# Repositories
from app.infrastructure.persistence.repositories import (
    SqlAnswerSheetRepository,
    SqlOCRResultRepository,
    SqlQuestionRepository,
    SqlQuestionMappingRepository,
    SqlAuditLogRepository,
)

# Services
from app.domain.services.default_question_detector import DefaultQuestionDetector
from app.domain.services.default_answer_segmenter import DefaultAnswerSegmenter
from app.domain.services.default_question_mapper import DefaultQuestionMapper

# Use Cases
from app.application.use_cases.ocr.process_question_mapping_use_case import ProcessQuestionMappingUseCase
from app.application.use_cases.ocr.get_question_mappings_use_case import GetQuestionMappingsUseCase
from app.application.use_cases.ocr.reprocess_question_mapping_use_case import ReprocessQuestionMappingUseCase

from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import EntityNotFoundException
from app.core.exceptions import not_found, bad_request

router = APIRouter(prefix="/ocr", tags=["Question Mappings"])


@router.get(
    "/{answer_sheet_id}/mappings",
    response_model=list[QuestionMappingResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Question Mappings",
    description="Teacher/Admin only. Retrieves the list of question mappings for a specific answer sheet."
)
async def get_question_mappings(
    answer_sheet_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> list[QuestionMappingResponse]:
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    question_mapping_repo = SqlQuestionMappingRepository(db)

    use_case = GetQuestionMappingsUseCase(answer_sheet_repo, question_mapping_repo)
    try:
        return await use_case.execute(answer_sheet_id)
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))


@router.post(
    "/{answer_sheet_id}/mappings/reprocess",
    response_model=list[QuestionMappingResponse],
    status_code=status.HTTP_200_OK,
    summary="Reprocess Question Mappings",
    description="Teacher/Admin only. Resets and re-runs the Question Detection, Answer Segmentation, and Question Mapping pipeline synchronously."
)
async def reprocess_question_mappings(
    answer_sheet_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> list[QuestionMappingResponse]:
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    ocr_result_repo = SqlOCRResultRepository(db)
    question_repo = SqlQuestionRepository(db)
    question_mapping_repo = SqlQuestionMappingRepository(db)
    audit_repo = SqlAuditLogRepository(db)

    detector = DefaultQuestionDetector()
    segmenter = DefaultAnswerSegmenter()
    mapper = DefaultQuestionMapper(question_repo)

    process_use_case = ProcessQuestionMappingUseCase(
        answer_sheet_repo=answer_sheet_repo,
        ocr_result_repo=ocr_result_repo,
        question_mapping_repo=question_mapping_repo,
        audit_repo=audit_repo,
        detector=detector,
        segmenter=segmenter,
        mapper=mapper
    )

    use_case = ReprocessQuestionMappingUseCase(question_mapping_repo, process_use_case)

    try:
        mappings = await use_case.execute(answer_sheet_id, user_id=current_user.id)
        await db.commit()
        return mappings
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except Exception as e:
        raise bad_request(str(e))


@router.get(
    "/{answer_sheet_id}/mapping-summary",
    response_model=QuestionMappingSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Question Mapping Summary",
    description="Teacher/Admin only. Returns count analytics for mapped, unmapped, duplicate, and unattempted questions."
)
async def get_question_mapping_summary(
    answer_sheet_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> QuestionMappingSummaryResponse:
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    question_repo = SqlQuestionRepository(db)
    question_mapping_repo = SqlQuestionMappingRepository(db)

    sheet = await answer_sheet_repo.get_by_id(answer_sheet_id)
    if not sheet:
        raise not_found("AnswerSheet", str(answer_sheet_id))

    # Fetch total questions in the exam
    questions = await question_repo.get_by_exam_id(sheet.exam_id)
    total_questions = len(questions)

    # Fetch mapping results
    mappings = await question_mapping_repo.list_by_answer_sheet_id(answer_sheet_id)

    mapped_count = sum(1 for m in mappings if m.status == "MAPPED")
    unmapped_count = sum(1 for m in mappings if m.status == "UNMAPPED")
    duplicate_count = sum(1 for m in mappings if m.status == "DUPLICATE_DETECTED")
    not_attempted_count = sum(1 for m in mappings if m.status == "NOT_ATTEMPTED")

    return QuestionMappingSummaryResponse(
        total_questions=total_questions,
        mapped_questions=mapped_count,
        unmapped_questions=unmapped_count,
        duplicate_questions=duplicate_count,
        not_attempted_questions=not_attempted_count
    )
