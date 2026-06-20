"""
0001_initial_schema — Initial Database Schema

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-06-20 12:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. roles table
    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name")
    )
    op.create_index("ix_roles_id", "roles", ["id"], unique=False)
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    # 2. users table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username")
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    # 3. teachers table
    op.create_table(
        "teachers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("employee_code", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_code"),
        sa.UniqueConstraint("user_id")
    )
    op.create_index("ix_teachers_id", "teachers", ["id"], unique=False)
    op.create_index("ix_teachers_employee_code", "teachers", ["employee_code"], unique=True)

    # 4. refresh_tokens table
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash")
    )
    op.create_index("ix_refresh_tokens_id", "refresh_tokens", ["id"], unique=False)
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)

    # 5. students table
    op.create_table(
        "students",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_number", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("class_section", sa.String(length=50), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("student_number")
    )
    op.create_index("ix_students_id", "students", ["id"], unique=False)
    op.create_index("ix_students_student_number", "students", ["student_number"], unique=True)

    # 6. subjects table
    op.create_table(
        "subjects",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code")
    )
    op.create_index("ix_subjects_id", "subjects", ["id"], unique=False)
    op.create_index("ix_subjects_code", "subjects", ["code"], unique=True)

    # 7. exams table
    op.create_table(
        "exams",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("subject_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("exam_date", sa.Date(), nullable=False),
        sa.Column("total_marks", sa.Integer(), nullable=False),
        sa.Column("passing_marks", sa.Integer(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("scoring_config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_exams_id", "exams", ["id"], unique=False)
    op.create_index("ix_exams_subject_id", "exams", ["subject_id"], unique=False)

    # 8. questions table
    op.create_table(
        "questions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("exam_id", sa.UUID(), nullable=False),
        sa.Column("question_number", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("marks", sa.Integer(), nullable=False),
        sa.Column("question_type", sa.String(length=50), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("exam_id", "question_number", name="uq_questions_exam_question")
    )
    op.create_index("ix_questions_id", "questions", ["id"], unique=False)
    op.create_index("ix_questions_exam_id", "questions", ["exam_id"], unique=False)

    # 9. model_answers table
    op.create_table(
        "model_answers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_id")
    )
    op.create_index("ix_model_answers_id", "model_answers", ["id"], unique=False)

    # 10. rubrics table
    op.create_table(
        "rubrics",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("total_weight", sa.Float(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("grading_mode", sa.String(length=50), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_id", "version", name="uq_rubrics_question_version")
    )
    op.create_index("ix_rubrics_id", "rubrics", ["id"], unique=False)
    op.create_index("ix_rubrics_is_active", "rubrics", ["is_active"], unique=False)
    op.create_index("ix_rubrics_question_id", "rubrics", ["question_id"], unique=False)

    # 11. rubric_criteria table
    op.create_table(
        "rubric_criteria",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("rubric_id", sa.UUID(), nullable=False),
        sa.Column("criterion_name", sa.String(length=255), nullable=False),
        sa.Column("criterion_description", sa.Text(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("max_marks", sa.Float(), nullable=False),
        sa.Column("expected_keywords", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["rubric_id"], ["rubrics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_rubric_criteria_id", "rubric_criteria", ["id"], unique=False)
    op.create_index("ix_rubric_criteria_rubric_id", "rubric_criteria", ["rubric_id"], unique=False)

    # 12. answer_sheets table
    op.create_table(
        "answer_sheets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("exam_id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("uploaded_by", sa.UUID(), nullable=False),
        sa.Column("original_filename", sa.String(length=500), nullable=False),
        sa.Column("stored_filename", sa.String(length=500), nullable=False),
        sa.Column("file_path", sa.String(length=1000), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_filename")
    )
    op.create_index("ix_answer_sheets_id", "answer_sheets", ["id"], unique=False)
    op.create_index("ix_answer_sheets_exam_id", "answer_sheets", ["exam_id"], unique=False)
    op.create_index("ix_answer_sheets_student_id", "answer_sheets", ["student_id"], unique=False)
    op.create_index("ix_answer_sheets_status", "answer_sheets", ["status"], unique=False)

    # 13. ocr_results table
    op.create_table(
        "ocr_results",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("answer_sheet_id", sa.UUID(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("structured_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("language_detected", sa.String(length=50), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("engine_version", sa.String(length=50), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["answer_sheet_id"], ["answer_sheets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("answer_sheet_id")
    )
    op.create_index("ix_ocr_results_id", "ocr_results", ["id"], unique=False)

    # 14. extracted_answers table
    op.create_table(
        "extracted_answers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("ocr_result_id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("answer_sheet_id", sa.UUID(), nullable=False),
        sa.Column("detected_question_number", sa.Integer(), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("extraction_confidence", sa.Float(), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("bounding_box", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["answer_sheet_id"], ["answer_sheets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ocr_result_id"], ["ocr_results.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_extracted_answers_id", "extracted_answers", ["id"], unique=False)
    op.create_index("ix_extracted_answers_answer_sheet_id", "extracted_answers", ["answer_sheet_id"], unique=False)
    op.create_index("ix_extracted_answers_ocr_result_id", "extracted_answers", ["ocr_result_id"], unique=False)
    op.create_index("ix_extracted_answers_question_id", "extracted_answers", ["question_id"], unique=False)

    # 15. evaluations table
    op.create_table(
        "evaluations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("answer_sheet_id", sa.UUID(), nullable=False),
        sa.Column("extracted_answer_id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("model_answer_id", sa.UUID(), nullable=False),
        sa.Column("rubric_id", sa.UUID(), nullable=True),
        sa.Column("ai_score", sa.Float(), nullable=True),
        sa.Column("max_marks", sa.Integer(), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=True),
        sa.Column("keyword_match_score", sa.Float(), nullable=True),
        sa.Column("ai_feedback", sa.Text(), nullable=True),
        sa.Column("teacher_score", sa.Float(), nullable=True),
        sa.Column("teacher_feedback", sa.Text(), nullable=True),
        sa.Column("final_score", sa.Float(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("verified_by", sa.UUID(), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evaluation_model", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["answer_sheet_id"], ["answer_sheets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["extracted_answer_id"], ["extracted_answers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["model_answer_id"], ["model_answers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rubric_id"], ["rubrics.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["verified_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("answer_sheet_id", "question_id", name="uq_evaluations_sheet_question"),
        sa.UniqueConstraint("extracted_answer_id")
    )
    op.create_index("ix_evaluations_id", "evaluations", ["id"], unique=False)
    op.create_index("ix_evaluations_answer_sheet_id", "evaluations", ["answer_sheet_id"], unique=False)
    op.create_index("ix_evaluations_question_id", "evaluations", ["question_id"], unique=False)

    # 16. evaluation_revisions table
    op.create_table(
        "evaluation_revisions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("evaluation_id", sa.UUID(), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("previous_score", sa.Float(), nullable=True),
        sa.Column("new_score", sa.Float(), nullable=False),
        sa.Column("previous_feedback", sa.Text(), nullable=True),
        sa.Column("new_feedback", sa.Text(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("changed_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_evaluation_revisions_id", "evaluation_revisions", ["id"], unique=False)
    op.create_index("ix_evaluation_revisions_evaluation_id", "evaluation_revisions", ["evaluation_id"], unique=False)

    # 17. criterion_evaluations table
    op.create_table(
        "criterion_evaluations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("evaluation_id", sa.UUID(), nullable=False),
        sa.Column("rubric_criterion_id", sa.UUID(), nullable=False),
        sa.Column("ai_score", sa.Float(), nullable=True),
        sa.Column("ai_semantic_score", sa.Float(), nullable=True),
        sa.Column("ai_keyword_score", sa.Float(), nullable=True),
        sa.Column("ai_feedback", sa.Text(), nullable=True),
        sa.Column("teacher_score", sa.Float(), nullable=True),
        sa.Column("teacher_feedback", sa.Text(), nullable=True),
        sa.Column("final_score", sa.Float(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rubric_criterion_id"], ["rubric_criteria.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evaluation_id", "rubric_criterion_id", name="uq_criterion_evaluations_eval_criterion")
    )
    op.create_index("ix_criterion_evaluations_id", "criterion_evaluations", ["id"], unique=False)
    op.create_index("ix_criterion_evaluations_evaluation_id", "criterion_evaluations", ["evaluation_id"], unique=False)

    # 18. final_results table
    op.create_table(
        "final_results",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("answer_sheet_id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("exam_id", sa.UUID(), nullable=False),
        sa.Column("total_marks_obtained", sa.Float(), nullable=False),
        sa.Column("total_marks_possible", sa.Integer(), nullable=False),
        sa.Column("percentage", sa.Float(), nullable=False),
        sa.Column("grade", sa.String(length=10), nullable=True),
        sa.Column("pass_fail_status", sa.String(length=50), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["answer_sheet_id"], ["answer_sheets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["published_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("answer_sheet_id")
    )
    op.create_index("ix_final_results_id", "final_results", ["id"], unique=False)
    op.create_index("ix_final_results_exam_id", "final_results", ["exam_id"], unique=False)
    op.create_index("ix_final_results_student_id", "final_results", ["student_id"], unique=False)
    op.create_index("ix_final_results_is_published", "final_results", ["is_published"], unique=False)

    # 19. plagiarism_reports table
    op.create_table(
        "plagiarism_reports",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("exam_id", sa.UUID(), nullable=False),
        sa.Column("source_answer_sheet_id", sa.UUID(), nullable=False),
        sa.Column("target_answer_sheet_id", sa.UUID(), nullable=False),
        sa.Column("similarity_percentage", sa.Float(), nullable=False),
        sa.Column("similarity_details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("flagged_questions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("reviewed_by", sa.UUID(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_answer_sheet_id"], ["answer_sheets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_answer_sheet_id"], ["answer_sheets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_plagiarism_reports_id", "plagiarism_reports", ["id"], unique=False)
    op.create_index("ix_plagiarism_reports_exam_id", "plagiarism_reports", ["exam_id"], unique=False)
    op.create_index("ix_plagiarism_reports_status", "plagiarism_reports", ["status"], unique=False)

    # 20. audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.UUID(), nullable=True),
        sa.Column("old_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("new_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"], unique=False)
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)

    # 21. notifications table
    op.create_table(
        "notifications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=True),
        sa.Column("resource_id", sa.UUID(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_notifications_id", "notifications", ["id"], unique=False)
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"], unique=False)
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"], unique=False)


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("audit_logs")
    op.drop_table("plagiarism_reports")
    op.drop_table("final_results")
    op.drop_table("criterion_evaluations")
    op.drop_table("evaluation_revisions")
    op.drop_table("evaluations")
    op.drop_table("extracted_answers")
    op.drop_table("ocr_results")
    op.drop_table("answer_sheets")
    op.drop_table("rubric_criteria")
    op.drop_table("rubrics")
    op.drop_table("model_answers")
    op.drop_table("questions")
    op.drop_table("exams")
    op.drop_table("subjects")
    op.drop_table("students")
    op.drop_table("refresh_tokens")
    op.drop_table("teachers")
    op.drop_table("users")
    op.drop_table("roles")
