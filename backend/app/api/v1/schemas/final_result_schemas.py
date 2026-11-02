"""
api/v1/schemas/final_result_schemas.py — Results Pydantic Schemas
"""

from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class FinalResultResponse(BaseModel):
    result_id: uuid.UUID = Field(..., validation_alias="id")
    exam_id: uuid.UUID
    student_id: uuid.UUID
    answer_sheet_id: uuid.UUID
    total_marks_obtained: float
    total_marks_possible: int
    percentage: float
    grade: str | None = None
    pass_fail_status: str
    is_published: bool
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class ExamResultsStudentItem(BaseModel):
    student_id: uuid.UUID
    student_name: str
    student_number: str
    marks_obtained: float
    percentage: float
    grade: str | None = None
    pass_fail_status: str
    verification_status: str
    publication_status: str


class ExamResultsResponse(BaseModel):
    exam_id: uuid.UUID
    exam_title: str
    total_marks: int
    passing_marks: int
    items: list[ExamResultsStudentItem]
    total_items: int
    page: int
    page_size: int
    total_pages: int


class StudentResultItem(BaseModel):
    exam_id: uuid.UUID
    exam_title: str
    subject_name: str
    percentage: float
    grade: str | None = None
    pass_fail_status: str
    published_status: str


class StudentResultsResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    student_number: str
    class_section: str | None = None
    history: list[StudentResultItem]


class ResultsDashboardResponse(BaseModel):
    total_students_evaluated: int
    total_results: int
    total_published: int
    pending_publication: int
    average_score: float
    pass_rate: float
    fail_rate: float


class DashboardOverviewResponse(BaseModel):
    total_answer_sheets: int
    pending_ocr: int
    pending_evaluation: int
    completed_evaluations: int
    teacher_review_pending: int
    plagiarism_alerts: int
    average_score: float
    average_processing_time: float

