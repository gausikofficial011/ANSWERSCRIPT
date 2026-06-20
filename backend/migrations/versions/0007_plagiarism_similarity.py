"""
0007_plagiarism_similarity — Create plagiarism_similarities and update plagiarism_reports/answer_sheets

Revision ID: 0007_plagiarism_similarity
Revises: 0006_update_evaluations_mapping
Create Date: 2026-06-20 18:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = "0007_plagiarism_similarity"
down_revision: Union[str, None] = "0006_update_evaluations_mapping"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create plagiarism_similarities table
    op.create_table(
        "plagiarism_similarities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_answer_sheet_id", sa.UUID(), nullable=False),
        sa.Column("target_answer_sheet_id", sa.UUID(), nullable=False),
        sa.Column("source_question_mapping_id", sa.UUID(), nullable=False),
        sa.Column("target_question_mapping_id", sa.UUID(), nullable=False),
        sa.Column("semantic_similarity", sa.Float(), nullable=False),
        sa.Column("lexical_similarity", sa.Float(), nullable=False),
        sa.Column("overlap_similarity", sa.Float(), nullable=False),
        sa.Column("final_similarity", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_answer_sheet_id"], ["answer_sheets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_answer_sheet_id"], ["answer_sheets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_question_mapping_id"], ["question_mappings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_question_mapping_id"], ["question_mappings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_question_mapping_id", "target_question_mapping_id", name="uq_plagiarism_similarities_pair")
    )
    
    # Indexes for plagiarism_similarities
    op.create_index("ix_plagiarism_similarities_id", "plagiarism_similarities", ["id"], unique=False)
    op.create_index("ix_plagiarism_similarities_source_mapping_id", "plagiarism_similarities", ["source_question_mapping_id"], unique=False)
    op.create_index("ix_plagiarism_similarities_target_mapping_id", "plagiarism_similarities", ["target_question_mapping_id"], unique=False)
    op.create_index("ix_plagiarism_similarities_final_similarity", "plagiarism_similarities", ["final_similarity"], unique=False)
    op.create_index("ix_plagiarism_similarities_source_sheet_id", "plagiarism_similarities", ["source_answer_sheet_id"], unique=False)
    op.create_index("ix_plagiarism_similarities_target_sheet_id", "plagiarism_similarities", ["target_answer_sheet_id"], unique=False)

    # 2. Alter plagiarism_reports table to add highest_similarity, risk_level, teacher_notes
    op.add_column("plagiarism_reports", sa.Column("highest_similarity", sa.Float(), nullable=False, server_default="0.0"))
    op.add_column("plagiarism_reports", sa.Column("risk_level", sa.String(length=50), nullable=False, server_default="CLEAN"))
    op.add_column("plagiarism_reports", sa.Column("teacher_notes", sa.Text(), nullable=True))
    op.create_unique_constraint("uq_plagiarism_reports_pair", "plagiarism_reports", ["source_answer_sheet_id", "target_answer_sheet_id"])
    
    # Indexes for plagiarism_reports
    op.create_index("ix_plagiarism_reports_source_sheet_id", "plagiarism_reports", ["source_answer_sheet_id"], unique=False)
    op.create_index("ix_plagiarism_reports_target_sheet_id", "plagiarism_reports", ["target_answer_sheet_id"], unique=False)
    op.create_index("ix_plagiarism_reports_risk_level", "plagiarism_reports", ["risk_level"], unique=False)

    # 3. Alter answer_sheets table to add plagiarism_flagged column
    op.add_column("answer_sheets", sa.Column("plagiarism_flagged", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    # Remove added columns from answer_sheets
    op.drop_column("answer_sheets", "plagiarism_flagged")

    # Remove added indexes and columns from plagiarism_reports
    op.drop_index("ix_plagiarism_reports_risk_level", table_name="plagiarism_reports")
    op.drop_index("ix_plagiarism_reports_target_sheet_id", table_name="plagiarism_reports")
    op.drop_index("ix_plagiarism_reports_source_sheet_id", table_name="plagiarism_reports")
    op.drop_constraint("uq_plagiarism_reports_pair", "plagiarism_reports", type_="unique")
    op.drop_column("plagiarism_reports", "teacher_notes")
    op.drop_column("plagiarism_reports", "risk_level")
    op.drop_column("plagiarism_reports", "highest_similarity")

    # Drop plagiarism_similarities table and indexes
    op.drop_index("ix_plagiarism_similarities_target_sheet_id", table_name="plagiarism_similarities")
    op.drop_index("ix_plagiarism_similarities_source_sheet_id", table_name="plagiarism_similarities")
    op.drop_index("ix_plagiarism_similarities_final_similarity", table_name="plagiarism_similarities")
    op.drop_index("ix_plagiarism_similarities_target_mapping_id", table_name="plagiarism_similarities")
    op.drop_index("ix_plagiarism_similarities_source_mapping_id", table_name="plagiarism_similarities")
    op.drop_index("ix_plagiarism_similarities_id", table_name="plagiarism_similarities")
    op.drop_table("plagiarism_similarities")
