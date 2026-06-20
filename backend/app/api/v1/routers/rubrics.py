"""
api/v1/routers/rubrics.py — Rubric Management Endpoints
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.api.v1.schemas.rubric_schemas import (
    RubricCreateRequest,
    RubricUpdateRequest,
    RubricResponse,
)
from app.api.v1.schemas.pagination_schemas import PaginatedSchemaResponse
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.core.pagination import PaginationParams
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.sql_rubric_repository import SqlRubricRepository
from app.infrastructure.persistence.repositories.sql_rubric_criterion_repository import SqlRubricCriterionRepository
from app.infrastructure.persistence.repositories.sql_question_repository import SqlQuestionRepository
from app.infrastructure.persistence.repositories.sql_audit_log_repository import SqlAuditLogRepository
from app.application.use_cases.rubrics import (
    CreateRubricUseCase,
    UpdateRubricUseCase,
    DeleteRubricUseCase,
    GetRubricUseCase,
    ListRubricsUseCase,
)
from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import (
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException,
)
from app.core.exceptions import not_found, duplicate_resource, bad_request

router = APIRouter(prefix="/rubrics", tags=["Rubrics"])


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
    response_model=RubricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Rubric",
    description="Admin/Teacher only. Define a grading rubric with criteria for a question."
)
async def create_rubric(
    payload: RubricCreateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> RubricResponse:
    rubric_repo = SqlRubricRepository(db)
    criterion_repo = SqlRubricCriterionRepository(db)
    question_repo = SqlQuestionRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = CreateRubricUseCase(rubric_repo, criterion_repo, question_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    criteria_data = [
        {
            "criterion_name": c.criterion_name,
            "criterion_description": c.criterion_description,
            "weight": c.weight,
            "max_marks": c.max_marks,
            "expected_keywords": c.expected_keywords,
            "order_index": c.order_index,
        }
        for c in payload.criteria
    ]

    try:
        rubric = await use_case.execute(
            question_id=payload.question_id,
            title=payload.title,
            total_weight=payload.total_weight,
            grading_mode=payload.grading_mode,
            criteria_data=criteria_data,
            created_by=current_user.id,
            description=payload.description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return rubric
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.get(
    "",
    response_model=PaginatedSchemaResponse[RubricResponse],
    status_code=status.HTTP_200_OK,
    summary="List Rubrics",
    description="Retrieve paginated rubrics, optionally filtered by question and active state."
)
async def list_rubrics(
    question_id: uuid.UUID | None = Query(None, description="Filter by question UUID."),
    is_active: bool | None = Query(None, description="Filter by active state."),
    pagination: PaginationParams = Depends(get_academic_pagination),
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> PaginatedSchemaResponse[RubricResponse]:
    rubric_repo = SqlRubricRepository(db)
    use_case = ListRubricsUseCase(rubric_repo)

    result = await use_case.execute(
        pagination=pagination,
        question_id=question_id,
        is_active=is_active
    )
    return result


@router.get(
    "/{id}",
    response_model=RubricResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Rubric By ID",
    description="Retrieve a specific grading rubric including its criteria."
)
async def get_rubric(
    id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> RubricResponse:
    rubric_repo = SqlRubricRepository(db)
    use_case = GetRubricUseCase(rubric_repo)

    try:
        rubric = await use_case.execute(id)
        return rubric
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))


@router.put(
    "/{id}",
    response_model=RubricResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Rubric",
    description="Admin/Teacher only. Updates rubric details. If locked, automatically provisions new active version."
)
async def update_rubric(
    id: uuid.UUID,
    payload: RubricUpdateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> RubricResponse:
    rubric_repo = SqlRubricRepository(db)
    criterion_repo = SqlRubricCriterionRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = UpdateRubricUseCase(rubric_repo, criterion_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    criteria_data = None
    if payload.criteria is not None:
        criteria_data = [
            {
                "criterion_name": c.criterion_name,
                "criterion_description": c.criterion_description,
                "weight": c.weight,
                "max_marks": c.max_marks,
                "expected_keywords": c.expected_keywords,
                "order_index": c.order_index,
            }
            for c in payload.criteria
        ]

    try:
        rubric = await use_case.execute(
            rubric_id=id,
            updater_id=current_user.id,
            title=payload.title,
            description=payload.description,
            total_weight=payload.total_weight,
            grading_mode=payload.grading_mode,
            criteria_data=criteria_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return rubric
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Rubric",
    description="Admin/Teacher only. Soft deletes rubric, provided it is not locked."
)
async def delete_rubric(
    id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
):
    rubric_repo = SqlRubricRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = DeleteRubricUseCase(rubric_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        success = await use_case.execute(
            rubric_id=id,
            deleter_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        if not success:
            raise bad_request("Failed to delete rubric.")
        return {"detail": "Rubric deleted successfully."}
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)
