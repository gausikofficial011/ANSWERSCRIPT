"""
api/v1/routers/exams.py — Exam Management Endpoints
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.api.v1.schemas.exam_schemas import (
    ExamCreateRequest,
    ExamUpdateRequest,
    ExamResponse,
)
from app.api.v1.schemas.pagination_schemas import PaginatedSchemaResponse
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, ExamStatus
from app.core.pagination import PaginationParams
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.sql_exam_repository import SqlExamRepository
from app.infrastructure.persistence.repositories.sql_subject_repository import SqlSubjectRepository
from app.infrastructure.persistence.repositories.sql_audit_log_repository import SqlAuditLogRepository
from app.application.use_cases.exams import (
    CreateExamUseCase,
    UpdateExamUseCase,
    DeleteExamUseCase,
    GetExamUseCase,
    ListExamsUseCase,
)
from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import (
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException,
)
from app.core.exceptions import not_found, duplicate_resource, bad_request

router = APIRouter(prefix="/exams", tags=["Exams"])


async def get_academic_pagination(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    page_size: int = Query(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"Items per page (max {MAX_PAGE_SIZE}).",
    ),
) -> PaginationParams:
    return PaginationParams(page=page, limit=page_size)


@router.post(
    "",
    response_model=ExamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Exam",
    description="Admin/Teacher only. Create a new exam and log audit event."
)
async def create_exam(
    payload: ExamCreateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> ExamResponse:
    exam_repo = SqlExamRepository(db)
    subject_repo = SqlSubjectRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = CreateExamUseCase(exam_repo, subject_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        exam = await use_case.execute(
            subject_id=payload.subject_id,
            title=payload.title,
            exam_date=payload.exam_date,
            total_marks=payload.total_marks,
            passing_marks=payload.passing_marks,
            created_by=current_user.id,
            description=payload.description,
            duration_minutes=payload.duration_minutes,
            status=payload.status,
            scoring_config=payload.scoring_config,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return exam
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.get(
    "",
    response_model=PaginatedSchemaResponse[ExamResponse],
    status_code=status.HTTP_200_OK,
    summary="List Exams",
    description="Retrieve paginated exams list, optionally filtered by subject, search, or status."
)
async def list_exams(
    search: str | None = Query(None, description="Search exams by title or description."),
    subject_id: uuid.UUID | None = Query(None, description="Filter by subject UUID."),
    status: ExamStatus | None = Query(None, description="Filter by exam status."),
    pagination: PaginationParams = Depends(get_academic_pagination),
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> PaginatedSchemaResponse[ExamResponse]:
    exam_repo = SqlExamRepository(db)
    use_case = ListExamsUseCase(exam_repo)

    result = await use_case.execute(
        pagination=pagination,
        search=search,
        subject_id=subject_id,
        status=status.value if status else None
    )
    return result


@router.get(
    "/{id}",
    response_model=ExamResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Exam By ID",
    description="Retrieve details of a single exam by its UUID."
)
async def get_exam(
    id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> ExamResponse:
    exam_repo = SqlExamRepository(db)
    use_case = GetExamUseCase(exam_repo)

    try:
        exam = await use_case.execute(id)
        return exam
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))


@router.put(
    "/{id}",
    response_model=ExamResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Exam",
    description="Admin/Teacher only. Update exam specifications and log audit event."
)
async def update_exam(
    id: uuid.UUID,
    payload: ExamUpdateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> ExamResponse:
    exam_repo = SqlExamRepository(db)
    subject_repo = SqlSubjectRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = UpdateExamUseCase(exam_repo, subject_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        exam = await use_case.execute(
            exam_id=id,
            updater_id=current_user.id,
            title=payload.title,
            exam_date=payload.exam_date,
            total_marks=payload.total_marks,
            passing_marks=payload.passing_marks,
            description=payload.description,
            duration_minutes=payload.duration_minutes,
            status=payload.status,
            scoring_config=payload.scoring_config,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return exam
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Exam",
    description="Admin/Teacher only. Soft delete exam and log audit event."
)
async def delete_exam(
    id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
):
    exam_repo = SqlExamRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = DeleteExamUseCase(exam_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        success = await use_case.execute(
            exam_id=id,
            deleter_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        if not success:
            raise bad_request("Failed to delete exam.")
        return {"detail": "Exam deleted successfully."}
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)
