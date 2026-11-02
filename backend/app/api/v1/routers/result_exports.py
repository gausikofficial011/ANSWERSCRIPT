"""
api/v1/routers/result_exports.py — Results CSV Exports API Router
"""

from __future__ import annotations
import uuid
import logging
from fastapi import APIRouter, Depends, status, HTTPException
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
from app.application.use_cases.results.export_exam_results_csv_use_case import ExportExamResultsCSVUseCase
from app.application.use_cases.results.export_student_results_csv_use_case import ExportStudentResultsCSVUseCase

from app.domain.exceptions.domain_exception import EntityNotFoundException
from app.core.exceptions import not_found, bad_request

logger = logging.getLogger("app.api.result_exports")

router = APIRouter(prefix="/results", tags=["Results CSV Exports"])


@router.get(
    "/exams/{exam_id}/export/csv",
    status_code=status.HTTP_200_OK,
    summary="Export Exam Results CSV",
    description="Teacher/Admin only. Stream a CSV file containing all student results for a specific exam."
)
async def export_exam_results_csv(
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

    export_use_case = ExportExamResultsCSVUseCase(get_exam_results_use_case)

    try:
        try:
            logger.info(f"OPERATIONAL_LOG: Exporting exam results CSV attempt. Exam={exam_id}, User={current_user.email}")
        except Exception:
            pass
        csv_data = await export_use_case.execute(exam_id=exam_id)
        try:
            logger.info(f"OPERATIONAL_LOG: Exported exam results CSV successfully. Exam={exam_id}, User={current_user.email}")
        except Exception:
            pass
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=exam_{exam_id}_results.csv"
            }
        )
    except EntityNotFoundException as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Exporting exam results CSV failed - Exam not found. Exam={exam_id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise not_found(e.entity_type, str(e.entity_id))
    except Exception as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Exporting exam results CSV failed. Exam={exam_id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise bad_request(str(e))


@router.get(
    "/students/{student_id}/export/csv",
    status_code=status.HTTP_200_OK,
    summary="Export Student Results CSV",
    description="Stream a CSV file containing a student's history profile results."
)
async def export_student_results_csv(
    student_id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> StreamingResponse:
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
                detail="Access denied. Students can only export their own results."
            )
        only_published = True

    get_student_results_use_case = GetStudentResultsUseCase(
        final_result_repo=final_result_repo,
        student_repo=student_repo,
        exam_repo=exam_repo,
        subject_repo=subject_repo
    )

    export_use_case = ExportStudentResultsCSVUseCase(get_student_results_use_case)

    try:
        try:
            logger.info(f"OPERATIONAL_LOG: Exporting student results CSV attempt. Student={student_id}, User={current_user.email}")
        except Exception:
            pass
        csv_data = await export_use_case.execute(student_id=student_id, only_published=only_published)
        try:
            logger.info(f"OPERATIONAL_LOG: Exported student results CSV successfully. Student={student_id}, User={current_user.email}")
        except Exception:
            pass
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=student_{student_id}_results.csv"
            }
        )
    except EntityNotFoundException as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Exporting student results CSV failed - Student not found. Student={student_id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise not_found(e.entity_type, str(e.entity_id))
    except Exception as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Exporting student results CSV failed. Student={student_id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise bad_request(str(e))
