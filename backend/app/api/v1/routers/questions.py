"""
api/v1/routers/questions.py — Question Management Endpoints
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.api.v1.schemas.question_schemas import (
    QuestionCreateRequest,
    QuestionUpdateRequest,
    QuestionResponse,
)
from app.api.v1.schemas.pagination_schemas import PaginatedSchemaResponse
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, QuestionType
from app.core.pagination import PaginationParams
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.sql_question_repository import SqlQuestionRepository
from app.infrastructure.persistence.repositories.sql_exam_repository import SqlExamRepository
from app.infrastructure.persistence.repositories.sql_audit_log_repository import SqlAuditLogRepository
from app.application.use_cases.questions import (
    CreateQuestionUseCase,
    UpdateQuestionUseCase,
    DeleteQuestionUseCase,
    GetQuestionUseCase,
    ListQuestionsUseCase,
)
from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import (
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException,
)
from app.core.exceptions import not_found, duplicate_resource, bad_request

router = APIRouter(prefix="/questions", tags=["Questions"])


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
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Question",
    description="Admin/Teacher only. Add a question to an exam and log audit event."
)
async def create_question(
    payload: QuestionCreateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> QuestionResponse:
    question_repo = SqlQuestionRepository(db)
    exam_repo = SqlExamRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = CreateQuestionUseCase(question_repo, exam_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        question = await use_case.execute(
            exam_id=payload.exam_id,
            question_number=payload.question_number,
            question_text=payload.question_text,
            marks=payload.marks,
            question_type=payload.question_type,
            created_by=current_user.id,
            language=payload.language,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return question
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except DuplicateEntityException as e:
        raise duplicate_resource(e.entity_type, e.field, str(e.value))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.get(
    "",
    response_model=PaginatedSchemaResponse[QuestionResponse],
    status_code=status.HTTP_200_OK,
    summary="List Questions",
    description="Retrieve paginated questions list, optionally filtered by exam or search."
)
async def list_questions(
    search: str | None = Query(None, description="Search questions by text."),
    exam_id: uuid.UUID | None = Query(None, description="Filter by exam UUID."),
    pagination: PaginationParams = Depends(get_academic_pagination),
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> PaginatedSchemaResponse[QuestionResponse]:
    question_repo = SqlQuestionRepository(db)
    use_case = ListQuestionsUseCase(question_repo)

    result = await use_case.execute(
        pagination=pagination,
        search=search,
        exam_id=exam_id
    )
    return result


@router.get(
    "/{id}",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Question By ID",
    description="Retrieve details of a single question by its UUID."
)
async def get_question(
    id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> QuestionResponse:
    question_repo = SqlQuestionRepository(db)
    use_case = GetQuestionUseCase(question_repo)

    try:
        question = await use_case.execute(id)
        return question
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))


@router.put(
    "/{id}",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Question",
    description="Admin/Teacher only. Update question parameters and log audit event."
)
async def update_question(
    id: uuid.UUID,
    payload: QuestionUpdateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> QuestionResponse:
    question_repo = SqlQuestionRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = UpdateQuestionUseCase(question_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        question = await use_case.execute(
            question_id=id,
            updater_id=current_user.id,
            question_number=payload.question_number,
            question_text=payload.question_text,
            marks=payload.marks,
            question_type=payload.question_type,
            language=payload.language,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return question
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except DuplicateEntityException as e:
        raise duplicate_resource(e.entity_type, e.field, str(e.value))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Question",
    description="Admin/Teacher only. Soft delete question and log audit event."
)
async def delete_question(
    id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
):
    question_repo = SqlQuestionRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = DeleteQuestionUseCase(question_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        success = await use_case.execute(
            question_id=id,
            deleter_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        if not success:
            raise bad_request("Failed to delete question.")
        return {"detail": "Question deleted successfully."}
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)
