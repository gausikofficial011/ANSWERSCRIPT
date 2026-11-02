"""
api/v1/routers/result_reports.py — Results PDF Reports API Router
"""

from __future__ import annotations
import uuid
import io
import logging
from fastapi import APIRouter, Depends, HTTPException, status

logger = logging.getLogger("app.api.result_reports")
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.infrastructure.persistence.database import get_db_session
from app.domain.entities.user import User
from app.core.constants import UserRole

# Repositories
from app.infrastructure.persistence.repositories import (
    SqlFinalResultRepository,
    SqlAnswerSheetRepository,
    SqlExamRepository,
    SqlStudentRepository,
    SqlSubjectRepository,
    SqlQuestionRepository,
    SqlEvaluationRepository
)

# Services & Use Cases
from app.application.services.final_result_synchronization_service import FinalResultSynchronizationService
from app.application.use_cases.results.get_exam_results_use_case import GetExamResultsUseCase
from app.application.use_cases.results.get_student_results_use_case import GetStudentResultsUseCase
from app.application.use_cases.results.generate_student_transcript_pdf_use_case import GenerateStudentTranscriptPDFUseCase
from app.application.use_cases.results.generate_exam_report_pdf_use_case import GenerateExamReportPDFUseCase
from app.infrastructure.reports.weasyprint_pdf_service import WeasyPrintPDFService

from app.domain.exceptions.domain_exception import EntityNotFoundException
from app.core.exceptions import not_found, bad_request

router = APIRouter(prefix="/results", tags=["Results PDF Reports"])


@router.get(
    "/students/{student_id}/transcript/pdf",
    status_code=status.HTTP_200_OK,
    summary="Get Student Transcript PDF",
    description="Authorized users (Teachers, Admins, or own student) only. Stream student's academic history transcript PDF."
)
async def get_student_transcript_pdf(
    student_id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> StreamingResponse:
    # 1. Enforce student-only authorization guard
    only_published = False
    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER):
        student_repo = SqlStudentRepository(db)
        student = await student_repo.get_by_email(current_user.email)
        if not student or student.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Students can only access their own transcript."
            )
        only_published = True

    # 2. Setup repos & use cases
    final_result_repo = SqlFinalResultRepository(db)
    student_repo = SqlStudentRepository(db)
    exam_repo = SqlExamRepository(db)
    subject_repo = SqlSubjectRepository(db)

    get_student_results_use_case = GetStudentResultsUseCase(
        final_result_repo=final_result_repo,
        student_repo=student_repo,
        exam_repo=exam_repo,
        subject_repo=subject_repo
    )

    pdf_service = WeasyPrintPDFService()
    use_case = GenerateStudentTranscriptPDFUseCase(
        get_student_results_use_case=get_student_results_use_case,
        pdf_service=pdf_service
    )

    try:
        try:
            logger.info(f"OPERATIONAL_LOG: Generating student transcript PDF attempt. Student={student_id}, User={current_user.email}")
        except Exception:
            pass
        pdf_bytes = await use_case.execute(student_id=student_id, only_published=only_published)
        try:
            logger.info(f"OPERATIONAL_LOG: Generated student transcript PDF successfully. Student={student_id}, User={current_user.email}")
        except Exception:
            pass
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=student_{student_id}_transcript.pdf"
            }
        )
    except EntityNotFoundException as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Generating student transcript PDF failed - Student not found. Student={student_id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise not_found(e.entity_type, str(e.entity_id))
    except Exception as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Generating student transcript PDF failed. Student={student_id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise bad_request(str(e))


@router.get(
    "/exams/{exam_id}/report/pdf",
    status_code=status.HTTP_200_OK,
    summary="Get Exam Report PDF",
    description="Teacher/Admin only. Stream a PDF of the exam summary report."
)
async def get_exam_report_pdf(
    exam_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> StreamingResponse:
    final_result_repo = SqlFinalResultRepository(db)
    answer_sheet_repo = SqlAnswerSheetRepository(db)
    exam_repo = SqlExamRepository(db)
    student_repo = SqlStudentRepository(db)
    question_repo = SqlQuestionRepository(db)
    evaluation_repo = SqlEvaluationRepository(db)
    subject_repo = SqlSubjectRepository(db)

    sync_service = FinalResultSynchronizationService(
        final_result_repo=final_result_repo,
        evaluation_repo=evaluation_repo,
        answer_sheet_repo=answer_sheet_repo,
        question_repo=question_repo,
        exam_repo=exam_repo
    )

    get_exam_results_use_case = GetExamResultsUseCase(
        final_result_repo=final_result_repo,
        answer_sheet_repo=answer_sheet_repo,
        exam_repo=exam_repo,
        student_repo=student_repo,
        sync_service=sync_service
    )

    pdf_service = WeasyPrintPDFService()
    use_case = GenerateExamReportPDFUseCase(
        get_exam_results_use_case=get_exam_results_use_case,
        exam_repo=exam_repo,
        subject_repo=subject_repo,
        pdf_service=pdf_service
    )

    try:
        try:
            logger.info(f"OPERATIONAL_LOG: Generating exam report PDF attempt. Exam={exam_id}, User={current_user.email}")
        except Exception:
            pass
        pdf_bytes = await use_case.execute(exam_id=exam_id)
        try:
            logger.info(f"OPERATIONAL_LOG: Generated exam report PDF successfully. Exam={exam_id}, User={current_user.email}")
        except Exception:
            pass
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=exam_{exam_id}_report.pdf"
            }
        )
    except EntityNotFoundException as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Generating exam report PDF failed - Exam not found. Exam={exam_id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise not_found(e.entity_type, str(e.entity_id))
    except Exception as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Generating exam report PDF failed. Exam={exam_id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise bad_request(str(e))
