"""
api/v1/routers/model_answers.py — ModelAnswer Management Endpoints
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.api.v1.schemas.model_answer_schemas import (
    ModelAnswerCreateRequest,
    ModelAnswerUpdateRequest,
    ModelAnswerResponse,
)
from app.api.v1.schemas.pagination_schemas import PaginatedSchemaResponse
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.core.pagination import PaginationParams
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.sql_model_answer_repository import SqlModelAnswerRepository
from app.infrastructure.persistence.repositories.sql_question_repository import SqlQuestionRepository
from app.infrastructure.persistence.repositories.sql_audit_log_repository import SqlAuditLogRepository
from app.application.use_cases.model_answers import (
    CreateModelAnswerUseCase,
    UpdateModelAnswerUseCase,
    DeleteModelAnswerUseCase,
    GetModelAnswerUseCase,
    ListModelAnswersUseCase,
)
from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import (
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException,
)
from app.core.exceptions import not_found, duplicate_resource, bad_request

router = APIRouter(prefix="/model-answers", tags=["Model Answers"])


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
    response_model=ModelAnswerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Model Answer",
    description="Admin/Teacher only. Associate a model answer with a question and log audit event."
)
async def create_model_answer(
    payload: ModelAnswerCreateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> ModelAnswerResponse:
    model_answer_repo = SqlModelAnswerRepository(db)
    question_repo = SqlQuestionRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = CreateModelAnswerUseCase(model_answer_repo, question_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        model_answer = await use_case.execute(
            question_id=payload.question_id,
            answer_text=payload.answer_text,
            created_by=current_user.id,
            keywords=payload.keywords,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return model_answer
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except DuplicateEntityException as e:
        raise duplicate_resource(e.entity_type, e.field, str(e.value))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.get(
    "",
    response_model=PaginatedSchemaResponse[ModelAnswerResponse],
    status_code=status.HTTP_200_OK,
    summary="List Model Answers",
    description="Retrieve paginated model answers list, optionally filtered by question ID."
)
async def list_model_answers(
    question_id: uuid.UUID | None = Query(None, description="Filter by question UUID."),
    pagination: PaginationParams = Depends(get_academic_pagination),
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> PaginatedSchemaResponse[ModelAnswerResponse]:
    model_answer_repo = SqlModelAnswerRepository(db)
    use_case = ListModelAnswersUseCase(model_answer_repo)

    result = await use_case.execute(
        pagination=pagination,
        question_id=question_id
    )
    return result


@router.get(
    "/{id}",
    response_model=ModelAnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Model Answer By ID",
    description="Retrieve details of a single model answer by its UUID."
)
async def get_model_answer(
    id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> ModelAnswerResponse:
    model_answer_repo = SqlModelAnswerRepository(db)
    use_case = GetModelAnswerUseCase(model_answer_repo)

    try:
        model_answer = await use_case.execute(id)
        return model_answer
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))


@router.put(
    "/{id}",
    response_model=ModelAnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Model Answer",
    description="Admin/Teacher only. Update model answer solutions and log audit event."
)
async def update_model_answer(
    id: uuid.UUID,
    payload: ModelAnswerUpdateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> ModelAnswerResponse:
    model_answer_repo = SqlModelAnswerRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = UpdateModelAnswerUseCase(model_answer_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        model_answer = await use_case.execute(
            model_answer_id=id,
            updater_id=current_user.id,
            answer_text=payload.answer_text,
            keywords=payload.keywords,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return model_answer
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Model Answer",
    description="Admin/Teacher only. Soft delete model answer and log audit event."
)
async def delete_model_answer(
    id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
):
    model_answer_repo = SqlModelAnswerRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = DeleteModelAnswerUseCase(model_answer_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        success = await use_case.execute(
            model_answer_id=id,
            deleter_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        if not success:
            raise bad_request("Failed to delete model answer.")
        return {"detail": "Model answer deleted successfully."}
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)
