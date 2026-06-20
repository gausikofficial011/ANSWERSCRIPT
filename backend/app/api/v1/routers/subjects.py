"""
api/v1/routers/subjects.py — Subject Management Endpoints
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.api.v1.schemas.subject_schemas import (
    SubjectCreateRequest,
    SubjectUpdateRequest,
    SubjectResponse,
)
from app.api.v1.schemas.pagination_schemas import PaginatedSchemaResponse
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.core.pagination import PaginationParams
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.sql_subject_repository import SqlSubjectRepository
from app.infrastructure.persistence.repositories.sql_audit_log_repository import SqlAuditLogRepository
from app.application.use_cases.subjects import (
    CreateSubjectUseCase,
    UpdateSubjectUseCase,
    DeleteSubjectUseCase,
    GetSubjectUseCase,
    ListSubjectsUseCase,
)
from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import (
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException,
)
from app.core.exceptions import not_found, duplicate_resource, bad_request

router = APIRouter(prefix="/subjects", tags=["Subjects"])


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
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Subject",
    description="Admin/Teacher only. Create a new academic subject and log audit event."
)
async def create_subject(
    payload: SubjectCreateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> SubjectResponse:
    subject_repo = SqlSubjectRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = CreateSubjectUseCase(subject_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        subject = await use_case.execute(
            name=payload.name,
            code=payload.code,
            created_by=current_user.id,
            description=payload.description,
            language=payload.language,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return subject
    except DuplicateEntityException as e:
        raise duplicate_resource(e.entity_type, e.field, str(e.value))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.get(
    "",
    response_model=PaginatedSchemaResponse[SubjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List Subjects",
    description="Retrieve a paginated list of subjects, optionally filtered by search query or activity state."
)
async def list_subjects(
    search: str | None = Query(None, description="Search subjects by name or code."),
    is_active: bool | None = Query(None, description="Filter by active state."),
    pagination: PaginationParams = Depends(get_academic_pagination),
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> PaginatedSchemaResponse[SubjectResponse]:
    subject_repo = SqlSubjectRepository(db)
    use_case = ListSubjectsUseCase(subject_repo)

    result = await use_case.execute(
        pagination=pagination,
        search=search,
        is_active=is_active
    )
    return result


@router.get(
    "/{id}",
    response_model=SubjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Subject By ID",
    description="Retrieve details of a single subject by its UUID."
)
async def get_subject(
    id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> SubjectResponse:
    subject_repo = SqlSubjectRepository(db)
    use_case = GetSubjectUseCase(subject_repo)

    try:
        subject = await use_case.execute(id)
        return subject
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))


@router.put(
    "/{id}",
    response_model=SubjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Subject",
    description="Admin/Teacher only. Update subject details and log audit event."
)
async def update_subject(
    id: uuid.UUID,
    payload: SubjectUpdateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> SubjectResponse:
    subject_repo = SqlSubjectRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = UpdateSubjectUseCase(subject_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        subject = await use_case.execute(
            subject_id=id,
            updater_id=current_user.id,
            name=payload.name,
            code=payload.code,
            description=payload.description,
            language=payload.language,
            is_active=payload.is_active,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return subject
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except DuplicateEntityException as e:
        raise duplicate_resource(e.entity_type, e.field, str(e.value))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Subject",
    description="Admin/Teacher only. Soft delete subject and log audit event."
)
async def delete_subject(
    id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
):
    subject_repo = SqlSubjectRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = DeleteSubjectUseCase(subject_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        success = await use_case.execute(
            subject_id=id,
            deleter_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        if not success:
            raise bad_request("Failed to delete subject.")
        return {"detail": "Subject deleted successfully."}
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)
