"""
0005_create_question_mappings — Create question_mappings table

Revision ID: 0005_create_question_mappings
Revises: 0004_page_wise_ocr_results
Create Date: 2026-06-20 16:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic.
revision: str = "0005_create_question_mappings"
down_revision: Union[str, None] = "0004_page_wise_ocr_results"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "question_mappings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("answer_sheet_id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=True),
        sa.Column("detected_question_number", sa.Integer(), nullable=True),
        sa.Column("detected_question_label", sa.String(length=100), nullable=True),
        sa.Column("extracted_answer_text", sa.Text(), nullable=False),
        sa.Column("start_page", sa.Integer(), nullable=True),
        sa.Column("end_page", sa.Integer(), nullable=True),
        sa.Column("mapping_confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("duplicate_question_flag", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("duplicate_group_id", sa.UUID(), nullable=True),
        sa.Column("source_ocr_result_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source_bounding_boxes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source_page_numbers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("answer_word_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("answer_character_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("answer_page_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("corrected_question_id", sa.UUID(), nullable=True),
        sa.Column("corrected_by_user_id", sa.UUID(), nullable=True),
        sa.Column("corrected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        
        sa.ForeignKeyConstraint(["answer_sheet_id"], ["answer_sheets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["corrected_question_id"], ["questions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["corrected_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_question_mappings_id", "question_mappings", ["id"], unique=False)
    op.create_index("ix_question_mappings_answer_sheet_id", "question_mappings", ["answer_sheet_id"], unique=False)
    op.create_index("ix_question_mappings_question_id", "question_mappings", ["question_id"], unique=False)


def downgrade() -> None:
    op.drop_table("question_mappings")
