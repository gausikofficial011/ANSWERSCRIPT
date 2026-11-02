"""
api/v1/routers/results.py — Results API Router
"""

from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.api.v1.schemas.final_result_schemas import (
    ResultsDashboardResponse,
    ExamResultsResponse,
    StudentResultsResponse,
    DashboardOverviewResponse
)
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel
from app.infrastructure.persistence.models.final_result_model import FinalResultModel
from app.core.constants import AnswerSheetStatus
from sqlalchemy import select, func

# Repositories
from app.infrastructure.persistence.repositories import (
    SqlFinalResultRepository,
    SqlAnswerSheetRepository,
    SqlExamRepository,
    SqlStudentRepository,
    SqlSubjectRepository,
    SqlQuestionRepository,
    SqlAuditLogRepository,
    SqlEvaluationRepository
)
from app.core.constants import UserRole

# Use Cases and Services
from app.application.services.final_result_synchronization_service import FinalResultSynchronizationService
from app.application.use_cases.results.get_results_dashboard_use_case import GetResultsDashboardUseCase
from app.application.use_cases.results.get_exam_results_use_case import GetExamResultsUseCase
from app.application.use_cases.results.get_student_results_use_case import GetStudentResultsUseCase
from app.application.use_cases.results.publish_exam_results_use_case import PublishExamResultsUseCase

from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException
from app.core.exceptions import not_found, bad_request

router = APIRouter(prefix="/results", tags=["Results Publishing & Reporting"])


@router.get(
    "/dashboard",
    response_model=ResultsDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Results Dashboard Stats",
    description="Retrieve high-level aggregated academic performance indicator summaries."
)
async def get_results_dashboard(
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> ResultsDashboardResponse:
    final_result_repo = SqlFinalResultRepository(db)
    use_case = GetResultsDashboardUseCase(final_result_repo)
    try:
        stats = await use_case.execute()
        return ResultsDashboardResponse(**stats)
    except Exception as e:
        raise bad_request(str(e))


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get E2E Dashboard Overview Stats",
    description="Retrieve aggregated counts and stats for answer sheet evaluation pipeline."
)
async def get_dashboard_overview(
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> DashboardOverviewResponse:
    try:
        # 1. Total answer sheets
        total_sheets_query = select(func.count(AnswerSheetModel.id)).where(AnswerSheetModel.deleted_at.is_(None))
        total_sheets = (await db.execute(total_sheets_query)).scalar() or 0

        # 2. Pending OCR: UPLOADED, QUEUED_FOR_OCR, OCR_PROCESSING
        pending_ocr_query = select(func.count(AnswerSheetModel.id)).where(
            AnswerSheetModel.deleted_at.is_(None),
            AnswerSheetModel.status.in_([
                AnswerSheetStatus.UPLOADED.value,
                AnswerSheetStatus.QUEUED_FOR_OCR.value,
                AnswerSheetStatus.OCR_PROCESSING.value
            ])
        )
        pending_ocr = (await db.execute(pending_ocr_query)).scalar() or 0

        # 3. Pending AI Evaluation: OCR_COMPLETED, QUESTION_DETECTION, ANSWER_SEGMENTATION, QUESTION_MAPPING, MAPPING_COMPLETED, EVALUATION_PROCESSING
        pending_eval_query = select(func.count(AnswerSheetModel.id)).where(
            AnswerSheetModel.deleted_at.is_(None),
            AnswerSheetModel.status.in_([
                AnswerSheetStatus.OCR_COMPLETED.value,
                AnswerSheetStatus.QUESTION_DETECTION.value,
                AnswerSheetStatus.ANSWER_SEGMENTATION.value,
                AnswerSheetStatus.QUESTION_MAPPING.value,
                AnswerSheetStatus.MAPPING_COMPLETED.value,
                AnswerSheetStatus.EVALUATION_PROCESSING.value
            ])
        )
        pending_eval = (await db.execute(pending_eval_query)).scalar() or 0

        # 4. Completed Evaluations: EVALUATION_COMPLETED, VERIFIED, PUBLISHED
        completed_eval_query = select(func.count(AnswerSheetModel.id)).where(
            AnswerSheetModel.deleted_at.is_(None),
            AnswerSheetModel.status.in_([
                AnswerSheetStatus.EVALUATION_COMPLETED.value,
                AnswerSheetStatus.VERIFIED.value,
                AnswerSheetStatus.PUBLISHED.value
            ])
        )
        completed_eval = (await db.execute(completed_eval_query)).scalar() or 0

        # 5. Teacher Review Pending: TEACHER_REVIEW_PENDING
        review_pending_query = select(func.count(AnswerSheetModel.id)).where(
            AnswerSheetModel.deleted_at.is_(None),
            AnswerSheetModel.status == AnswerSheetStatus.TEACHER_REVIEW_PENDING.value
        )
        review_pending = (await db.execute(review_pending_query)).scalar() or 0

        # 6. Plagiarism Alerts
        plagiarism_query = select(func.count(AnswerSheetModel.id)).where(
            AnswerSheetModel.deleted_at.is_(None),
            AnswerSheetModel.plagiarism_flagged.is_(True)
        )
        plagiarism_alerts = (await db.execute(plagiarism_query)).scalar() or 0

        # 7. Average Score
        avg_score_query = select(func.avg(FinalResultModel.percentage))
        avg_score = float((await db.execute(avg_score_query)).scalar() or 0.0)

        # 8. Processing Time (Average of processing_completed_at - processing_started_at in seconds)
        proc_time_query = select(AnswerSheetModel.processing_started_at, AnswerSheetModel.processing_completed_at).where(
            AnswerSheetModel.deleted_at.is_(None),
            AnswerSheetModel.processing_started_at.is_not(None),
            AnswerSheetModel.processing_completed_at.is_not(None)
        )
        proc_times = (await db.execute(proc_time_query)).all()
        total_seconds = 0.0
        valid_counts = 0
        for started, completed in proc_times:
            if started and completed:
                diff = (completed - started).total_seconds()
                if diff > 0:
                    total_seconds += diff
                    valid_counts += 1
        avg_proc_time = (total_seconds / valid_counts) if valid_counts > 0 else 0.0

        return DashboardOverviewResponse(
            total_answer_sheets=total_sheets,
            pending_ocr=pending_ocr,
            pending_evaluation=pending_eval,
            completed_evaluations=completed_eval,
            teacher_review_pending=review_pending,
            plagiarism_alerts=plagiarism_alerts,
            average_score=avg_score,
            average_processing_time=avg_proc_time
        )
    except Exception as e:
        raise bad_request(str(e))



@router.get(
    "/exams/{exam_id}",
    response_model=ExamResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Exam Results List",
    description="Retrieve paginated list of student final grades and marks for a specific exam."
)
async def get_exam_results(
    exam_id: uuid.UUID,
    page: int = Query(default=1, ge=1, description="Page number."),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page."),
    search: str | None = Query(default=None, description="Search by student name or number."),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> ExamResultsResponse:
    final_result_repo = SqlFinalResultRepository(db)
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    exam_repo = SqlExamRepository(db)
    student_repo = SqlStudentRepository(db)
    question_repo = SqlQuestionRepository(db)
    evaluation_repo = SqlEvaluationRepository(db)

    # Construct score sync service
    sync_service = FinalResultSynchronizationService(
        final_result_repo=final_result_repo,
        evaluation_repo=evaluation_repo,
        answer_sheet_repo=answer_sheet_repo,
        question_repo=question_repo,
        exam_repo=exam_repo
    )

    use_case = GetExamResultsUseCase(
        final_result_repo=final_result_repo,
        answer_sheet_repo=answer_sheet_repo,
        exam_repo=exam_repo,
        student_repo=student_repo,
        sync_service=sync_service
    )

    try:
        results = await use_case.execute(
            exam_id=exam_id,
            page=page,
            page_size=page_size,
            search=search
        )
        return ExamResultsResponse(**results)
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except Exception as e:
        raise bad_request(str(e))


@router.get(
    "/students/{student_id}",
    response_model=StudentResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Student Results History",
    description="Retrieve academic grades and performance history for a specific student."
)
async def get_student_results(
    student_id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> StudentResultsResponse:
    final_result_repo = SqlFinalResultRepository(db)
    student_repo = SqlStudentRepository(db)
    exam_repo = SqlExamRepository(db)
    subject_repo = SqlSubjectRepository(db)

    only_published = False
    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER):
        student = await student_repo.get_by_email(current_user.email)
        if not student or student.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Students can only access their own results."
            )
        only_published = True

    use_case = GetStudentResultsUseCase(
        final_result_repo=final_result_repo,
        student_repo=student_repo,
        exam_repo=exam_repo,
        subject_repo=subject_repo
    )

    try:
        history = await use_case.execute(student_id, only_published=only_published)
        return StudentResultsResponse(**history)
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except Exception as e:
        raise bad_request(str(e))


@router.post(
    "/exams/{exam_id}/publish",
    status_code=status.HTTP_200_OK,
    summary="Publish Exam Results",
    description="Teacher only. Release verified scores and aggregate grades for a scheduled exam."
)
async def publish_exam_results(
    exam_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    final_result_repo = SqlFinalResultRepository(db)
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    exam_repo = SqlExamRepository(db)
    audit_repo = SqlAuditLogRepository(db)

    use_case = PublishExamResultsUseCase(
        final_result_repo=final_result_repo,
        answer_sheet_repo=answer_sheet_repo,
        exam_repo=exam_repo,
        audit_repo=audit_repo
    )

    try:
        result = await use_case.execute(exam_id=exam_id, publisher_id=current_user.id)
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
