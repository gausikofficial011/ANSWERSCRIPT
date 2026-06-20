"""
0002_add_soft_delete_to_academic — Add soft delete columns to Question, ModelAnswer, and Rubric tables

Revision ID: 0002_add_soft_delete_to_academic
Revises: 0001_initial_schema
Create Date: 2026-06-20 13:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision: str = "0002_add_soft_delete_to_academic"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("model_answers", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("rubrics", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("rubrics", "deleted_at")
    op.drop_column("model_answers", "deleted_at")
    op.drop_column("questions", "deleted_at")
