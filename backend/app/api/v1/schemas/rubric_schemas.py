"""
api/v1/schemas/rubric_schemas.py — Rubric and Rubric Criteria Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, field_validator
from app.core.constants import GradingMode, MAX_KEYWORDS_PER_CRITERION


class RubricCriterionCreate(BaseModel):
    criterion_name: str = Field(..., min_length=2, max_length=255, description="Short name (e.g. Concept Clarity)")
    criterion_description: str | None = Field(None, description="Detailed explanation of what this criterion evaluates")
    weight: float = Field(..., gt=0.0, le=1.0, description="Relative weight of this criterion in the rubric (between 0.0 and 1.0)")
    max_marks: float = Field(..., gt=0.0, description="Maximum marks assigned to this criterion")
    expected_keywords: list[str] = Field(default_factory=list, description="Keywords/phrases for matching (max 20)")
    order_index: int = Field(0, ge=0, description="Sorting and display sequence order")

    @field_validator("expected_keywords")
    @classmethod
    def validate_keywords(cls, v: list[str]) -> list[str]:
        if len(v) > MAX_KEYWORDS_PER_CRITERION:
            raise ValueError(f"expected_keywords cannot exceed {MAX_KEYWORDS_PER_CRITERION} items.")
        return v


class RubricCriterionUpdate(BaseModel):
    id: uuid.UUID | None = Field(None, description="Provide ID to update existing criterion, or omit to create new")
    criterion_name: str | None = Field(None, min_length=2, max_length=255)
    criterion_description: str | None = None
    weight: float | None = Field(None, gt=0.0, le=1.0)
    max_marks: float | None = Field(None, gt=0.0)
    expected_keywords: list[str] | None = None
    order_index: int | None = Field(None, ge=0)

    @field_validator("expected_keywords")
    @classmethod
    def validate_keywords(cls, v: list[str] | None) -> list[str] | None:
        if v is not None and len(v) > MAX_KEYWORDS_PER_CRITERION:
            raise ValueError(f"expected_keywords cannot exceed {MAX_KEYWORDS_PER_CRITERION} items.")
        return v


class RubricCreateRequest(BaseModel):
    question_id: uuid.UUID = Field(..., description="Foreign key link to Exam Question")
    title: str = Field(..., min_length=2, max_length=255, description="Rubric identifier name")
    description: str | None = Field(None, description="Optional description of the marking schema")
    total_weight: float = Field(1.0, gt=0.0, description="Rubric total weight (typically 1.0 or question total marks)")
    grading_mode: GradingMode = Field(GradingMode.AI, description="AI, MANUAL, or HYBRID grading mode")
    criteria: list[RubricCriterionCreate] = Field(..., description="List of criteria defining this rubric")

    @model_validator(mode="after")
    def validate_criteria_weights(self) -> RubricCreateRequest:
        if not self.criteria:
            raise ValueError("A Rubric must contain at least one criterion.")
        
        criteria_sum = sum(c.weight for c in self.criteria)
        if abs(criteria_sum - self.total_weight) > 1e-9:
            raise ValueError(
                f"Sum of criteria weights ({criteria_sum}) "
                f"does not match rubric total_weight ({self.total_weight})."
            )
        return self


class RubricUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    total_weight: float | None = Field(None, gt=0.0)
    grading_mode: GradingMode | None = None
    criteria: list[RubricCriterionUpdate] | None = Field(None, description="If provided, will replace/update the criteria list")

    @model_validator(mode="after")
    def validate_updated_criteria(self) -> RubricUpdateRequest:
        # Note: If criteria or total_weight are updated, we will validate the matching weights in the use case
        # since we need access to the existing weights for criteria that are NOT modified/deleted.
        return self


class RubricCriterionResponse(BaseModel):
    id: uuid.UUID
    rubric_id: uuid.UUID
    criterion_name: str
    criterion_description: str | None
    weight: float
    max_marks: float
    expected_keywords: list[str]
    order_index: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RubricResponse(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    title: str
    description: str | None
    total_weight: float
    version: int
    is_active: bool
    grading_mode: GradingMode
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    criteria: list[RubricCriterionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
