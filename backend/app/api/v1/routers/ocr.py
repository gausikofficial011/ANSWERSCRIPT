"""
api/v1/routers/ocr.py — OCR Pipeline REST API Endpoints
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_teacher
from app.api.v1.schemas.ocr_schemas import OCRResultResponse, DocumentExtractionResponse
from app.api.v1.schemas.answer_sheet_schemas import AnswerSheetResponse
from app.infrastructure.persistence.database import get_db_session
from app.application.services.document_extraction_service import DocumentExtractionService

# Repositories
from app.infrastructure.persistence.repositories import (
    SqlAnswerSheetRepository,
    SqlOCRResultRepository,
    SqlAuditLogRepository,
)

# Services / Use cases
from app.application.use_cases.ocr.get_ocr_result_use_case import GetOCRResultUseCase
from app.application.use_cases.ocr.reprocess_ocr_use_case import ReprocessOCRUseCase

from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import EntityNotFoundException
from app.core.exceptions import not_found, bad_request

router = APIRouter(prefix="/ocr", tags=["OCR Engine"])


@router.get(
    "/{answer_sheet_id}/results",
    response_model=list[OCRResultResponse],
    status_code=status.HTTP_200_OK,
    summary="Get OCR Results",
    description="Teacher/Admin only. Retrieves the page-wise OCR results, including extracted text, confidence, and bounding boxes."
)
async def get_ocr_results(
    answer_sheet_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> list[OCRResultResponse]:
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    ocr_result_repo = SqlOCRResultRepository(db)

    use_case = GetOCRResultUseCase(answer_sheet_repo, ocr_result_repo)
    try:
        results = await use_case.execute(answer_sheet_id)
        return results
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))


@router.post(
    "/{answer_sheet_id}/reprocess",
    response_model=AnswerSheetResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Reprocess Answer Sheet OCR",
    description="Teacher/Admin only. Resets the answer sheet's processing state, deletes previous results, and enqueues the OCR background task."
)
async def reprocess_ocr(
    answer_sheet_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> AnswerSheetResponse:
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    ocr_result_repo = SqlOCRResultRepository(db)
    audit_repo = SqlAuditLogRepository(db)

    use_case = ReprocessOCRUseCase(
        answer_sheet_repo=answer_sheet_repo,
        ocr_result_repo=ocr_result_repo,
        audit_repo=audit_repo
    )
    try:
        sheet = await use_case.execute(answer_sheet_id, user_id=current_user.id)
        await db.commit()
        return sheet
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))
    except Exception as e:
        raise bad_request(str(e))


@router.post(
    "/extract-document",
    response_model=DocumentExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract Text and Questions from PDF / Scanned Image (OCR)",
    description="Teacher/Admin only. Parses PDF digital text or executes EasyOCR vision pipeline on scanned pages/images, extracting questions, keywords, and model answers."
)
async def extract_document(
    file: UploadFile = File(..., description="Target PDF or Image (PNG, JPG, JPEG)"),
    extract_mode: str = Form("auto", description="Extraction mode: auto, ocr_only, or digital_only"),
    current_user: User = Depends(require_teacher),
) -> DocumentExtractionResponse:
    if not file.filename:
        raise bad_request("File name must not be empty.")

    file_bytes = await file.read()
    if not file_bytes:
        raise bad_request("Uploaded file is empty.")

    service = DocumentExtractionService()
    try:
        return await service.extract_from_file_bytes(
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            extract_mode=extract_mode
        )
    except Exception as e:
        raise bad_request(f"Document extraction failed: {str(e)}")
