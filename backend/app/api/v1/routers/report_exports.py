"""
api/v1/routers/report_exports.py — Evaluation & Plagiarism PDF Report Exports API Router
"""

from __future__ import annotations
import uuid
import io
import logging
from fastapi import APIRouter, Depends, HTTPException, status

logger = logging.getLogger("app.api.report_exports")
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.infrastructure.persistence.database import get_db_session
from app.domain.entities.user import User
from app.core.constants import UserRole

# Repositories
from app.infrastructure.persistence.repositories import (
    SqlEvaluationRepository,
    SqlAnswerSheetRepository,
    SqlStudentRepository,
    SqlExamRepository,
    SqlRubricCriterionRepository,
    SqlCriterionEvaluationRepository,
    SqlEvaluationRevisionRepository,
    SqlUserRepository,
    SqlPlagiarismRepository,
    SqlPlagiarismSimilarityRepository,
    SqlQuestionMappingRepository,
)

# Services & Use Cases
from app.application.use_cases.reports.generate_evaluation_report_pdf_use_case import GenerateEvaluationReportPDFUseCase
from app.application.use_cases.reports.generate_plagiarism_report_pdf_use_case import GeneratePlagiarismReportPDFUseCase
from app.infrastructure.reports.weasyprint_pdf_service import WeasyPrintPDFService
from app.infrastructure.reports.report_registry import report_registry

from app.domain.exceptions.domain_exception import EntityNotFoundException

router = APIRouter(tags=["Report PDF Exports"])


@router.get(
    "/evaluations/{id}/report/pdf",
    status_code=status.HTTP_200_OK,
    summary="Get Evaluation Detailed PDF Report",
    description="Authorized users (Teachers, Admins, or own student) only. Stream evaluation detailed PDF report."
)
async def get_evaluation_report_pdf(
    id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> StreamingResponse:
    # 1. Fetch Evaluation to check existence
    eval_repo = SqlEvaluationRepository(db)
    evaluation = await eval_repo.get_by_id(id)
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with id {id} not found."
        )

    # 2. Enforce authorization guard (Teacher/Admin, or own student)
    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER):
        answer_sheet_repo = SqlAnswerSheetRepository(db)
        answer_sheet = await answer_sheet_repo.get_by_id(evaluation.answer_sheet_id)
        if not answer_sheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer sheet for evaluation not found."
            )
        
        student_repo = SqlStudentRepository(db)
        student = await student_repo.get_by_email(current_user.email)
        if not student or student.id != answer_sheet.student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Students can only access their own evaluation report."
            )

    # 3. Generate PDF
    pdf_service = WeasyPrintPDFService()
    use_case = GenerateEvaluationReportPDFUseCase(
        evaluation_repo=eval_repo,
        answer_sheet_repo=SqlAnswerSheetRepository(db),
        student_repo=SqlStudentRepository(db),
        exam_repo=SqlExamRepository(db),
        rubric_criterion_repo=SqlRubricCriterionRepository(db),
        criterion_evaluation_repo=SqlCriterionEvaluationRepository(db),
        evaluation_revision_repo=SqlEvaluationRevisionRepository(db),
        user_repo=SqlUserRepository(db),
        pdf_service=pdf_service
    )

    try:
        try:
            logger.info(f"OPERATIONAL_LOG: Generating evaluation report PDF attempt. Evaluation={id}, User={current_user.email}")
        except Exception:
            pass
        pdf_bytes = await use_case.execute(evaluation_id=id)
        
        # 4. Register generation event in ReportRegistry
        report_registry.register(
            report_type="evaluation_report",
            requesting_user_id=current_user.id,
            file_size_bytes=len(pdf_bytes),
            metadata={"evaluation_id": str(id)}
        )
        try:
            logger.info(f"OPERATIONAL_LOG: Generated evaluation report PDF successfully. Evaluation={id}, User={current_user.email}")
        except Exception:
            pass

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=evaluation_{id}_report.pdf"
            }
        )
    except EntityNotFoundException as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Generating evaluation report PDF failed - Evaluation not found. Evaluation={id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{e.entity_type} not found."
        )
    except Exception as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Generating evaluation report PDF failed. Evaluation={id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/plagiarism/reports/{id}/export/pdf",
    status_code=status.HTTP_200_OK,
    summary="Get Plagiarism Comparison PDF Report",
    description="Teacher/Admin only. Stream plagiarism comparison PDF report."
)
async def get_plagiarism_report_pdf(
    id: uuid.UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> StreamingResponse:
    # 1. Fetch Plagiarism Report to check existence
    plagiarism_repo = SqlPlagiarismRepository(db)
    report = await plagiarism_repo.get_by_id(id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PlagiarismReport with id {id} not found."
        )

    # 2. Generate PDF
    pdf_service = WeasyPrintPDFService()
    use_case = GeneratePlagiarismReportPDFUseCase(
        plagiarism_repo=plagiarism_repo,
        plagiarism_similarity_repo=SqlPlagiarismSimilarityRepository(db),
        answer_sheet_repo=SqlAnswerSheetRepository(db),
        student_repo=SqlStudentRepository(db),
        question_mapping_repo=SqlQuestionMappingRepository(db),
        user_repo=SqlUserRepository(db),
        pdf_service=pdf_service
    )

    try:
        try:
            logger.info(f"OPERATIONAL_LOG: Generating plagiarism report PDF attempt. Report={id}, User={current_user.email}")
        except Exception:
            pass
        pdf_bytes = await use_case.execute(report_id=id)

        # 3. Register generation event in ReportRegistry
        report_registry.register(
            report_type="plagiarism_report",
            requesting_user_id=current_user.id,
            file_size_bytes=len(pdf_bytes),
            metadata={"report_id": str(id)}
        )
        try:
            logger.info(f"OPERATIONAL_LOG: Generated plagiarism report PDF successfully. Report={id}, User={current_user.email}")
        except Exception:
            pass

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=plagiarism_report_{id}.pdf"
            }
        )
    except EntityNotFoundException as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Generating plagiarism report PDF failed - Report not found. Report={id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{e.entity_type} not found."
        )
    except Exception as e:
        try:
            logger.error(f"OPERATIONAL_LOG: Generating plagiarism report PDF failed. Report={id}, User={current_user.email}, Error={str(e)}")
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
