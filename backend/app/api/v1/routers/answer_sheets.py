"""
api/v1/routers/answer_sheets.py — Answer Sheet Routing Endpoints
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status, Query, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.api.v1.schemas.answer_sheet_schemas import (
    AnswerSheetResponse,
    AnswerSheetListResponse,
)
from app.api.v1.schemas.pagination_schemas import PaginatedSchemaResponse
from app.api.v1.schemas.evaluation_schemas import EvaluationResponse
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.core.pagination import PaginationParams
from app.infrastructure.persistence.database import get_db_session

# Repositories
from app.infrastructure.persistence.repositories.sql_answer_sheet_repository import SqlAnswerSheetRepository
from app.infrastructure.persistence.repositories.sql_exam_repository import SqlExamRepository
from app.infrastructure.persistence.repositories.sql_student_repository import SqlStudentRepository
from app.infrastructure.persistence.repositories.sql_audit_log_repository import SqlAuditLogRepository

# Services
from app.infrastructure.storage.local_file_storage_service import LocalFileStorageService
from app.infrastructure.storage.file_validator_service import FileValidatorService
from app.infrastructure.storage.file_metadata_service import FileMetadataService
from app.infrastructure.storage.stub_malware_scanner import StubMalwareScanner
from app.infrastructure.storage.default_student_mapping_service import DefaultStudentMappingService

# Use Cases
from app.application.use_cases.answer_sheets import (
    UploadAnswerSheetUseCase,
    DeleteAnswerSheetUseCase,
    GetAnswerSheetUseCase,
    ListAnswerSheetsUseCase,
)

from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import (
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException,
)
from app.domain.exceptions.file_exceptions import (
    FileTooLargeException,
    UnsupportedFileTypeException,
    CorruptedFileException,
    EmptyFileException,
)
from app.core.exceptions import (
    not_found,
    duplicate_resource,
    bad_request,
    file_too_large,
    unsupported_file_type,
)

router = APIRouter(prefix="/answer-sheets", tags=["Answer Sheets"])


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
    "/upload",
    response_model=list[AnswerSheetResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload Answer Sheet Files",
    description="Admin/Teacher only. Upload single or multiple answer sheets for an exam. Matches sheets to students."
)
async def upload_answer_sheets(
    request: Request,
    exam_id: uuid.UUID = Form(..., description="Target exam UUID"),
    student_id: uuid.UUID | None = Form(None, description="Optional manual student mapping ID"),
    files: list[UploadFile] = File(..., description="Multipart files (PDF, PNG, JPG, JPEG)"),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> list[AnswerSheetResponse]:
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    exam_repo = SqlExamRepository(db)
    student_repo = SqlStudentRepository(db)
    audit_repo = SqlAuditLogRepository(db)

    # Instantiate services
    storage_service = LocalFileStorageService()
    validator_service = FileValidatorService()
    metadata_service = FileMetadataService()
    scanner = StubMalwareScanner()
    mapping_service = DefaultStudentMappingService(student_repo)

    use_case = UploadAnswerSheetUseCase(
        answer_sheet_repo=answer_sheet_repo,
        exam_repo=exam_repo,
        student_repo=student_repo,
        audit_repo=audit_repo,
        storage_service=storage_service,
        validator_service=validator_service,
        metadata_service=metadata_service,
        scanner=scanner,
        mapping_service=mapping_service
    )

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    uploaded_sheets = []
    for upload_file in files:
        try:
            # Read file bytes in memory
            file_data = await upload_file.read()
            
            sheet = await use_case.execute(
                exam_id=exam_id,
                filename=upload_file.filename or "unknown",
                file_data=file_data,
                uploaded_by=current_user.id,
                manual_student_id=student_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            uploaded_sheets.append(sheet)
        except EntityNotFoundException as e:
            raise not_found(e.entity_type, str(e.entity_id))
        except DuplicateEntityException as e:
            raise duplicate_resource(e.entity_type, e.field, str(e.value))
        except FileTooLargeException as e:
            # Enforce 50MB error response
            raise file_too_large(50)
        except UnsupportedFileTypeException as e:
            raise unsupported_file_type(e.context.get("allowed_types", []))
        except (EmptyFileException, CorruptedFileException) as e:
            raise bad_request(str(e))
        except BusinessRuleViolationException as e:
            raise bad_request(e.rule)
            
    return uploaded_sheets


@router.get(
    "",
    response_model=AnswerSheetListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Answer Sheets",
    description="Retrieve a paginated, searchable and filtered list of answer sheets."
)
async def list_answer_sheets(
    exam_id: uuid.UUID | None = Query(None, description="Filter by exam UUID."),
    student_id: uuid.UUID | None = Query(None, description="Filter by student UUID."),
    status: str | None = Query(None, description="Filter by file processing status."),
    search: str | None = Query(None, description="Search by original filename."),
    pagination: PaginationParams = Depends(get_academic_pagination),
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> AnswerSheetListResponse:
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    use_case = ListAnswerSheetsUseCase(answer_sheet_repo)

    result = await use_case.execute(
        pagination=pagination,
        exam_id=exam_id,
        student_id=student_id,
        status=status,
        search=search
    )
    return result


@router.get(
    "/{id}",
    response_model=AnswerSheetResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Answer Sheet By ID",
    description="Retrieve full metadata of a single answer sheet by its UUID."
)
async def get_answer_sheet(
    id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> AnswerSheetResponse:
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    use_case = GetAnswerSheetUseCase(answer_sheet_repo)

    try:
        sheet = await use_case.execute(id)
        return sheet
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Answer Sheet",
    description="Admin/Teacher only. Soft deletes answer sheet and log audit event."
)
async def delete_answer_sheet(
    id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
):
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    use_case = DeleteAnswerSheetUseCase(answer_sheet_repo, audit_repo)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        success = await use_case.execute(
            answer_sheet_id=id,
            deleter_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        if not success:
            raise bad_request("Failed to delete answer sheet.")
        return {"detail": "Answer sheet deleted successfully."}
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))


@router.get(
    "/{id}/evaluations",
    response_model=list[EvaluationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Answer Sheet Evaluations",
    description="Retrieve all question evaluations associated with a specific answer sheet."
)
async def get_answer_sheet_evaluations(
    id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> list[EvaluationResponse]:
    from app.infrastructure.persistence.repositories.sql_evaluation_repository import SqlEvaluationRepository
    from app.api.v1.schemas.evaluation_schemas import EvaluationResponse
    
    eval_repo = SqlEvaluationRepository(db)
    try:
        evals = await eval_repo.get_by_answer_sheet_id(id)
        return [EvaluationResponse.model_validate(ev) for ev in evals]
    except Exception as e:
        raise bad_request(str(e))
