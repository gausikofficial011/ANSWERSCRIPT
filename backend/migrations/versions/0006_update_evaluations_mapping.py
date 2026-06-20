"""
0006_update_evaluations_mapping — Update evaluations table columns

Revision ID: 0006_update_evaluations_mapping
Revises: 0005_create_question_mappings
Create Date: 2026-06-20 17:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic.
revision: str = "0006_update_evaluations_mapping"
down_revision: Union[str, None] = "0005_create_question_mappings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Drop constraints/foreign key pointing to extracted_answers from evaluations
    # In postgres, unique constraints and foreign keys are dropped by their constraint name.
    # Standard names: "evaluations_extracted_answer_id_fkey", "evaluations_extracted_answer_id_key"
    op.drop_constraint("evaluations_extracted_answer_id_fkey", "evaluations", type_="foreignkey")
    op.drop_constraint("evaluations_extracted_answer_id_key", "evaluations", type_="unique")
    
    # 2. Drop the extracted_answer_id column
    op.drop_column("evaluations", "extracted_answer_id")
    
    # 3. Add question_mapping_id column (nullable first, then populate/constrain, or make nullable=False since it is a test run)
    op.add_column("evaluations", sa.Column("question_mapping_id", sa.UUID(), nullable=False))
    
    # 4. Add constraints for question_mapping_id
    op.create_foreign_key(
        "evaluations_question_mapping_id_fkey",
        "evaluations",
        "question_mappings",
        ["question_mapping_id"],
        ["id"],
        ondelete="CASCADE"
    )
    op.create_unique_constraint(
        "uq_evaluations_question_mapping",
        "evaluations",
        ["question_mapping_id"]
    )
    
    # 5. Add evaluation_confidence and explanation columns
    op.add_column("evaluations", sa.Column("evaluation_confidence", sa.Float(), nullable=True))
    op.add_column("evaluations", sa.Column("explanation", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column("evaluations", "explanation")
    op.drop_column("evaluations", "evaluation_confidence")
    op.drop_constraint("uq_evaluations_question_mapping", "evaluations", type_="unique")
    op.drop_constraint("evaluations_question_mapping_id_fkey", "evaluations", type_="foreignkey")
    op.drop_column("evaluations", "question_mapping_id")
    
    op.add_column("evaluations", sa.Column("extracted_answer_id", sa.UUID(), nullable=False))
    op.create_unique_constraint("evaluations_extracted_answer_id_key", "evaluations", ["extracted_answer_id"])
    op.create_foreign_key(
        "evaluations_extracted_answer_id_fkey",
        "evaluations",
        "extracted_answers",
        ["extracted_answer_id"],
        ["id"],
        ondelete="CASCADE"
    )
