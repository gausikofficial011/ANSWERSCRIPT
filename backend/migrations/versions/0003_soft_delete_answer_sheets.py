"""
0003_soft_delete_answer_sheets — Add soft delete, hashing, supersession, and processing columns to answer_sheets

Revision ID: 0003_soft_delete_answer_sheets
Revises: 0002_add_soft_delete_to_academic
Create Date: 2026-06-20 14:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision: str = "0003_soft_delete_answer_sheets"
down_revision: Union[str, None] = "0002_add_soft_delete_to_academic"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adding new columns
    op.add_column("answer_sheets", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("answer_sheets", sa.Column("file_hash", sa.String(length=64), nullable=False, server_default=""))
    op.add_column("answer_sheets", sa.Column("supersedes_answer_sheet_id", sa.UUID(), nullable=True))
    op.add_column("answer_sheets", sa.Column("superseded_by_answer_sheet_id", sa.UUID(), nullable=True))
    op.add_column("answer_sheets", sa.Column("processing_status", sa.String(length=50), nullable=False, server_default="UPLOADED"))
    op.add_column("answer_sheets", sa.Column("queued_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("answer_sheets", sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("answer_sheets", sa.Column("processing_completed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("answer_sheets", sa.Column("failure_reason", sa.Text(), nullable=True))

    # Foreign key constraints
    op.create_foreign_key(
        "fk_answer_sheets_supersedes",
        "answer_sheets",
        "answer_sheets",
        ["supersedes_answer_sheet_id"],
        ["id"],
        ondelete="SET NULL"
    )
    op.create_foreign_key(
        "fk_answer_sheets_superseded_by",
        "answer_sheets",
        "answer_sheets",
        ["superseded_by_answer_sheet_id"],
        ["id"],
        ondelete="SET NULL"
    )

    # Index on file_hash
    op.create_index("ix_answer_sheets_file_hash", "answer_sheets", ["file_hash"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_answer_sheets_file_hash", table_name="answer_sheets")
    op.drop_constraint("fk_answer_sheets_superseded_by", "answer_sheets", type_="foreignkey")
    op.drop_constraint("fk_answer_sheets_supersedes", "answer_sheets", type_="foreignkey")
    
    op.drop_column("answer_sheets", "failure_reason")
    op.drop_column("answer_sheets", "processing_completed_at")
    op.drop_column("answer_sheets", "processing_started_at")
    op.drop_column("answer_sheets", "queued_at")
    op.drop_column("answer_sheets", "processing_status")
    op.drop_column("answer_sheets", "superseded_by_answer_sheet_id")
    op.drop_column("answer_sheets", "supersedes_answer_sheet_id")
    op.drop_column("answer_sheets", "file_hash")
    op.drop_column("answer_sheets", "deleted_at")
