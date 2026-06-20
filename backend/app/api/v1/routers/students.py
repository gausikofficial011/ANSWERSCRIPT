"""
api/v1/routers/students.py — Student Management Endpoints
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.api.v1.schemas.student_schemas import (
    StudentCreateRequest,
    StudentUpdateRequest,
    StudentResponse,
)
from app.api.v1.schemas.pagination_schemas import PaginatedSchemaResponse
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.core.pagination import PaginationParams
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories.sql_student_repository import SqlStudentRepository
from app.infrastructure.persistence.repositories.sql_audit_log_repository import SqlAuditLogRepository
from app.application.use_cases.students import (
    CreateStudentUseCase,
    UpdateStudentUseCase,
    DeleteStudentUseCase,
    GetStudentUseCase,
    ListStudentsUseCase,
)
from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import (
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException,
)
from app.core.exceptions import not_found, duplicate_resource, bad_request

router = APIRouter(prefix="/students", tags=["Students"])


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
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Student",
    description="Admin/Teacher only. Register a new student and log audit event."
)
async def create_student(
    payload: StudentCreateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> StudentResponse:
    student_repo = SqlStudentRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = CreateStudentUseCase(student_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        student = await use_case.execute(
            student_number=payload.student_number,
            full_name=payload.full_name,
            creator_id=current_user.id,
            email=payload.email,
            class_section=payload.class_section,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return student
    except DuplicateEntityException as e:
        raise duplicate_resource(e.entity_type, e.field, str(e.value))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.get(
    "",
    response_model=PaginatedSchemaResponse[StudentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Students",
    description="Retrieve paginated students list, filtered by search query or section batch."
)
async def list_students(
    search: str | None = Query(None, description="Search students by name, email or student number."),
    class_section: str | None = Query(None, description="Filter by section batch."),
    pagination: PaginationParams = Depends(get_academic_pagination),
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> PaginatedSchemaResponse[StudentResponse]:
    student_repo = SqlStudentRepository(db)
    use_case = ListStudentsUseCase(student_repo)

    result = await use_case.execute(
        pagination=pagination,
        search=search,
        class_section=class_section
    )
    return result


@router.get(
    "/{id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Student By ID",
    description="Retrieve details of a single student by their UUID."
)
async def get_student(
    id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> StudentResponse:
    student_repo = SqlStudentRepository(db)
    use_case = GetStudentUseCase(student_repo)

    try:
        student = await use_case.execute(id)
        return student
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))


@router.put(
    "/{id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Student",
    description="Admin/Teacher only. Update student records and log audit event."
)
async def update_student(
    id: uuid.UUID,
    payload: StudentUpdateRequest,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> StudentResponse:
    student_repo = SqlStudentRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = UpdateStudentUseCase(student_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        student = await use_case.execute(
            student_id=id,
            updater_id=current_user.id,
            student_number=payload.student_number,
            full_name=payload.full_name,
            email=payload.email,
            class_section=payload.class_section,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return student
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except DuplicateEntityException as e:
        raise duplicate_resource(e.entity_type, e.field, str(e.value))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Student",
    description="Admin/Teacher only. Soft delete student and log audit event."
)
async def delete_student(
    id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
):
    student_repo = SqlStudentRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = DeleteStudentUseCase(student_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        success = await use_case.execute(
            student_id=id,
            deleter_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        if not success:
            raise bad_request("Failed to delete student.")
        return {"detail": "Student deleted successfully."}
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        raise bad_request(e.rule)
