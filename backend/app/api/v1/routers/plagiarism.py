"""
api/v1/routers/plagiarism.py — Plagiarism Detection REST API Endpoints
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.api.v1.schemas.plagiarism_schemas import (
    PlagiarismReportResponse,
    PlagiarismSimilarityResponse,
    PlagiarismReviewRequest
)
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories import (
    SqlPlagiarismRepository,
    SqlPlagiarismSimilarityRepository,
    SqlAnswerSheetRepository,
    SqlAuditLogRepository
)
from app.application.use_cases.plagiarism.get_plagiarism_report_use_case import GetPlagiarismReportUseCase
from app.application.use_cases.plagiarism.review_plagiarism_use_case import ReviewPlagiarismUseCase
from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException
from app.core.exceptions import not_found, bad_request

router = APIRouter(prefix="/plagiarism", tags=["Plagiarism Detection"])


@router.get(
    "/reports",
    response_model=list[PlagiarismReportResponse],
    status_code=status.HTTP_200_OK,
    summary="List Plagiarism Reports",
    description="Retrieve all plagiarism reports, optionally filtered by exam_id."
)
async def list_plagiarism_reports(
    exam_id: uuid.UUID | None = None,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> list[PlagiarismReportResponse]:
    plagiarism_repo = SqlPlagiarismRepository(db)
    similarity_repo = SqlPlagiarismSimilarityRepository(db)
    
    use_case = GetPlagiarismReportUseCase(plagiarism_repo, similarity_repo)
    
    try:
        if exam_id:
            reports = await use_case.get_by_exam_id(exam_id)
        else:
            reports = await use_case.list_all_reports()
        return [PlagiarismReportResponse.model_validate(r) for r in reports]
    except Exception as e:
        raise bad_request(str(e))


@router.get(
    "/exams/{exam_id}/summary",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get Exam Plagiarism Summary",
    description="Retrieve a high-level plagiarism statistics and metrics summary for a specific exam."
)
async def get_exam_plagiarism_summary(
    exam_id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    plagiarism_repo = SqlPlagiarismRepository(db)
    similarity_repo = SqlPlagiarismSimilarityRepository(db)
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    
    use_case = GetPlagiarismReportUseCase(
        plagiarism_repo=plagiarism_repo,
        plagiarism_similarity_repo=similarity_repo,
        answer_sheet_repo=answer_sheet_repo
    )
    
    try:
        summary = await use_case.get_exam_summary(exam_id)
        return summary
    except Exception as e:
        raise bad_request(str(e))


@router.get(
    "/{answer_sheet_id}",
    response_model=list[PlagiarismReportResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Answer Sheet Plagiarism Reports",
    description="Retrieve plagiarism reports involving a specific answer sheet."
)
async def get_answer_sheet_reports(
    answer_sheet_id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> list[PlagiarismReportResponse]:
    plagiarism_repo = SqlPlagiarismRepository(db)
    similarity_repo = SqlPlagiarismSimilarityRepository(db)
    
    use_case = GetPlagiarismReportUseCase(plagiarism_repo, similarity_repo)
    
    try:
        reports = await use_case.get_by_answer_sheet_id(answer_sheet_id)
        return [PlagiarismReportResponse.model_validate(r) for r in reports]
    except Exception as e:
        raise bad_request(str(e))


@router.get(
    "/{report_id}/similarities",
    response_model=list[PlagiarismSimilarityResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Plagiarism Report Similarities",
    description="Retrieve question-level similarity details for a plagiarism report."
)
async def get_report_similarities(
    report_id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> list[PlagiarismSimilarityResponse]:
    plagiarism_repo = SqlPlagiarismRepository(db)
    similarity_repo = SqlPlagiarismSimilarityRepository(db)
    
    use_case = GetPlagiarismReportUseCase(plagiarism_repo, similarity_repo)
    
    try:
        similarities = await use_case.get_similarities(report_id)
        return [PlagiarismSimilarityResponse.model_validate(s) for s in similarities]
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except Exception as e:
        raise bad_request(str(e))


@router.post(
    "/{report_id}/review",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Review Plagiarism Report",
    description="Teacher only. Mark a plagiarism report as CONFIRMED_PLAGIARISM, FALSE_POSITIVE, or DISMISSED."
)
async def review_plagiarism_report(
    report_id: uuid.UUID,
    payload: PlagiarismReviewRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    plagiarism_repo = SqlPlagiarismRepository(db)
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    
    use_case = ReviewPlagiarismUseCase(
        plagiarism_repo=plagiarism_repo,
        answer_sheet_repo=answer_sheet_repo,
        audit_repo=audit_repo
    )
    
    try:
        result = await use_case.execute(
            report_id=report_id,
            status=payload.status,
            teacher_notes=payload.teacher_notes,
            user_id=current_user.id
        )
        await db.commit()
        return result
    except EntityNotFoundException as e:
        await db.rollback()
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        await db.rollback()
        raise bad_request(e.rule)
    except Exception as e:
        await db.rollback()
        raise bad_request(str(e))
