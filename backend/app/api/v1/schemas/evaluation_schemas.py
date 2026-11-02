"""
api/v1/schemas/evaluation_schemas.py — AI Evaluation Pydantic Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class CriterionEvaluationResponse(BaseModel):
    id: uuid.UUID
    evaluation_id: uuid.UUID
    rubric_criterion_id: uuid.UUID
    ai_score: float | None = None
    ai_semantic_score: float | None = None
    ai_keyword_score: float | None = None
    ai_feedback: str | None = None
    teacher_score: float | None = None
    teacher_feedback: str | None = None
    final_score: float | None = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EvaluationRevisionResponse(BaseModel):
    id: uuid.UUID
    evaluation_id: uuid.UUID
    revision_number: int
    previous_score: float | None = None
    new_score: float
    previous_feedback: str | None = None
    new_feedback: str | None = None
    reason: str
    changed_by: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ExplanationResponse(BaseModel):
    strengths: str
    weaknesses: str
    missing_topics: list[str]
    improvement_suggestions: str
    scoring_reasoning: str


class EvaluationResponse(BaseModel):
    id: uuid.UUID
    answer_sheet_id: uuid.UUID
    question_mapping_id: uuid.UUID
    question_id: uuid.UUID
    model_answer_id: uuid.UUID
    rubric_id: uuid.UUID | None = None
    max_marks: int
    ai_score: float | None = None
    similarity_score: float | None = None
    keyword_match_score: float | None = None
    ai_feedback: str | None = None
    teacher_score: float | None = None
    teacher_feedback: str | None = None
    final_score: float | None = None
    is_verified: bool
    verified_by: uuid.UUID | None = None
    verified_at: datetime | None = None
    evaluation_model: str | None = None
    evaluation_confidence: float | None = None
    confidence_score: float | None = None
    low_confidence_flag: bool = False
    explanation: ExplanationResponse | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CriterionOverride(BaseModel):
    rubric_criterion_id: uuid.UUID
    teacher_score: float = Field(..., ge=0.0)
    teacher_feedback: str | None = None


class VerifyEvaluationRequest(BaseModel):
    teacher_score: float = Field(..., ge=0.0)
    teacher_feedback: str | None = None
    reason: str = Field(..., min_length=3, max_length=500)
    criterion_overrides: list[CriterionOverride] | None = None


class DetailedEvaluationResponse(BaseModel):
    evaluation: EvaluationResponse
    criteria_evaluations: list[CriterionEvaluationResponse] = []
    revisions: list[EvaluationRevisionResponse] = []
