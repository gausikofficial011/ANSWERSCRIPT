"""
api/v1/routers/evaluations.py — Evaluation REST API Endpoints
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import require_auth, require_teacher
from app.api.v1.schemas.evaluation_schemas import (
    EvaluationResponse,
    DetailedEvaluationResponse,
    VerifyEvaluationRequest,
    ExplanationResponse,
)
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories import (
    SqlEvaluationRepository,
    SqlEvaluationRevisionRepository,
    SqlCriterionEvaluationRepository,
    SqlQuestionMappingRepository,
    SqlQuestionRepository,
    SqlModelAnswerRepository,
    SqlRubricRepository,
    SqlAnswerSheetRepository,
    SqlAuditLogRepository,
    SqlStudentRepository
)
from app.core.constants import UserRole
from app.application.use_cases.evaluations.evaluate_answer_use_case import EvaluateAnswerUseCase
from app.application.use_cases.evaluations.get_evaluation_use_case import GetEvaluationUseCase
from app.application.use_cases.evaluations.verify_evaluation_use_case import VerifyEvaluationUseCase
from app.application.use_cases.evaluations.re_evaluate_use_case import ReEvaluateUseCase

from app.domain.entities.user import User
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException
from app.core.exceptions import not_found, bad_request

router = APIRouter(prefix="/evaluations", tags=["AI Evaluations"])


@router.get(
    "/{id}",
    response_model=DetailedEvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Evaluation Details",
    description="Retrieve details of a single question evaluation including criteria scores and historical revisions."
)
async def get_evaluation(
    id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> DetailedEvaluationResponse:
    eval_repo = SqlEvaluationRepository(db)
    rev_repo = SqlEvaluationRevisionRepository(db)
    crit_repo = SqlCriterionEvaluationRepository(db)
    
    # Enforce student ownership check
    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER):
        evaluation = await eval_repo.get_by_id(id)
        if not evaluation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found.")
        
        sheet_repo = SqlAnswerSheetRepository(db)
        answer_sheet = await sheet_repo.get_by_id(evaluation.answer_sheet_id)
        if not answer_sheet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer sheet not found.")
        
        student_repo = SqlStudentRepository(db)
        student = await student_repo.get_by_email(current_user.email)
        if not student or student.id != answer_sheet.student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Students can only access their own evaluations."
            )

    use_case = GetEvaluationUseCase(
        evaluation_repo=eval_repo,
        revision_repo=rev_repo,
        criterion_eval_repo=crit_repo
    )

    try:
        result = await use_case.execute(id)
        # Convert domain entities to response structures
        return DetailedEvaluationResponse(
            evaluation=EvaluationResponse.model_validate(result["evaluation"]),
            criteria_evaluations=[c for c in result["criteria_evaluations"]],
            revisions=[r for r in result["revisions"]]
        )
    except EntityNotFoundException as e:
        raise not_found(e.entity_type, str(e.entity_id))


@router.get(
    "/answer-sheets/{answer_sheet_id}",
    response_model=list[EvaluationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Answer Sheet Evaluations",
    description="Retrieve all question evaluations associated with a specific answer sheet."
)
async def get_answer_sheet_evaluations(
    answer_sheet_id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> list[EvaluationResponse]:
    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER):
        sheet_repo = SqlAnswerSheetRepository(db)
        answer_sheet = await sheet_repo.get_by_id(answer_sheet_id)
        if not answer_sheet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer sheet not found.")
        
        student_repo = SqlStudentRepository(db)
        student = await student_repo.get_by_email(current_user.email)
        if not student or student.id != answer_sheet.student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Students can only access evaluations for their own answer sheet."
            )

    eval_repo = SqlEvaluationRepository(db)
    
    try:
        evals = await eval_repo.get_by_answer_sheet_id(answer_sheet_id)
        return [EvaluationResponse.model_validate(ev) for ev in evals]
    except Exception as e:
        raise bad_request(str(e))


@router.post(
    "/{id}/verify",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Evaluation & Score Override",
    description="Teacher only. Submit verification review, optional score override comments and per-criterion weights overrides."
)
async def verify_evaluation(
    id: uuid.UUID,
    payload: VerifyEvaluationRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> EvaluationResponse:
    eval_repo = SqlEvaluationRepository(db)
    rev_repo = SqlEvaluationRevisionRepository(db)
    crit_repo = SqlCriterionEvaluationRepository(db)
    rubric_repo = SqlRubricRepository(db)
    sheet_repo = SqlAnswerSheetRepository(db)
    audit_repo = SqlAuditLogRepository(db)
    
    use_case = VerifyEvaluationUseCase(
        evaluation_repo=eval_repo,
        revision_repo=rev_repo,
        criterion_eval_repo=crit_repo,
        rubric_repo=rubric_repo,
        answer_sheet_repo=sheet_repo,
        audit_repo=audit_repo
    )

    try:
        criterion_overrides = [co.model_dump() for co in payload.criterion_overrides] if payload.criterion_overrides else None
        
        evaluation = await use_case.execute(
            evaluation_id=id,
            teacher_score=payload.teacher_score,
            teacher_feedback=payload.teacher_feedback,
            verifier_id=current_user.id,
            reason=payload.reason,
            criterion_overrides=criterion_overrides
        )
        await db.commit()
        return EvaluationResponse.model_validate(evaluation)
    except EntityNotFoundException as e:
        await db.rollback()
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        await db.rollback()
        raise bad_request(e.rule)
    except Exception as e:
        await db.rollback()
        raise bad_request(str(e))


@router.post(
    "/{id}/re-evaluate",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Re-evaluate Student Answer",
    description="Teacher only. Re-run AI similarity & keyword matching scorer engine, producing a new scoring revision history."
)
async def re_evaluate_evaluation(
    id: uuid.UUID,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db_session)
) -> EvaluationResponse:
    eval_repo = SqlEvaluationRepository(db)
    rev_repo = SqlEvaluationRevisionRepository(db)
    crit_repo = SqlCriterionEvaluationRepository(db)
    mapping_repo = SqlQuestionMappingRepository(db)
    question_repo = SqlQuestionRepository(db)
    model_answer_repo = SqlModelAnswerRepository(db)
    rubric_repo = SqlRubricRepository(db)
    audit_repo = SqlAuditLogRepository(db)

    evaluate_answer_use_case = EvaluateAnswerUseCase(
        evaluation_repo=eval_repo,
        revision_repo=rev_repo,
        criterion_eval_repo=crit_repo,
        question_mapping_repo=mapping_repo,
        question_repo=question_repo,
        model_answer_repo=model_answer_repo,
        rubric_repo=rubric_repo,
        audit_repo=audit_repo
    )
    
    use_case = ReEvaluateUseCase(
        evaluation_repo=eval_repo,
        audit_repo=audit_repo,
        evaluate_answer_use_case=evaluate_answer_use_case
    )

    try:
        evaluation = await use_case.execute(
            evaluation_id=id,
            user_id=current_user.id
        )
        await db.commit()
        return EvaluationResponse.model_validate(evaluation)
    except EntityNotFoundException as e:
        await db.rollback()
        raise not_found(e.entity_type, str(e.entity_id))
    except BusinessRuleViolationException as e:
        await db.rollback()
        raise bad_request(e.rule)
    except Exception as e:
        await db.rollback()
        raise bad_request(str(e))


@router.get(
    "/{id}/explanation",
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Evaluation Explanation",
    description="Retrieve explainable scoring details (strengths, weaknesses, suggestions, missing topics)."
)
async def get_evaluation_explanation(
    id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db_session)
) -> ExplanationResponse:
    eval_repo = SqlEvaluationRepository(db)
    
    evaluation = await eval_repo.get_by_id(id)
    if not evaluation:
        raise not_found("Evaluation", str(id))

    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER):
        sheet_repo = SqlAnswerSheetRepository(db)
        answer_sheet = await sheet_repo.get_by_id(evaluation.answer_sheet_id)
        if not answer_sheet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer sheet not found.")
        
        student_repo = SqlStudentRepository(db)
        student = await student_repo.get_by_email(current_user.email)
        if not student or student.id != answer_sheet.student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Students can only access their own evaluation explanations."
            )

    exp = evaluation.explanation or {}
    return ExplanationResponse(
        strengths=exp.get("strengths", ""),
        weaknesses=exp.get("weaknesses", ""),
        missing_topics=exp.get("missing_topics", []),
        improvement_suggestions=exp.get("improvement_suggestions", ""),
        scoring_reasoning=exp.get("scoring_reasoning", "")
    )
