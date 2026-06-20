"""
0004_page_wise_ocr_results — Alter ocr_results to page-wise layout and tracking

Revision ID: 0004_page_wise_ocr_results
Revises: 0003_add_soft_delete_to_answer_sheets
Create Date: 2026-06-20 15:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic.
revision: str = "0004_page_wise_ocr_results"
down_revision: Union[str, None] = "0003_add_soft_delete_to_answer_sheets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Drop existing unique constraint on answer_sheet_id
    op.drop_constraint("ocr_results_answer_sheet_id_key", "ocr_results", type_="unique")

    # 2. Add new columns
    op.add_column("ocr_results", sa.Column("page_number", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("ocr_results", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("ocr_results", sa.Column("bounding_boxes", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("ocr_results", sa.Column("low_confidence_flag", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("ocr_results", sa.Column("average_confidence", sa.Float(), nullable=True))
    op.add_column("ocr_results", sa.Column("words_detected", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("ocr_results", sa.Column("processing_time", sa.Float(), nullable=True))
    op.add_column("ocr_results", sa.Column("ocr_engine_version", sa.String(length=50), nullable=True))
    op.add_column("ocr_results", sa.Column("preprocessing_version", sa.String(length=50), nullable=True))
    op.add_column("ocr_results", sa.Column("original_image_path", sa.String(length=1000), nullable=True))
    op.add_column("ocr_results", sa.Column("processed_image_path", sa.String(length=1000), nullable=True))
    op.add_column("ocr_results", sa.Column("status", sa.String(length=50), nullable=False, server_default="OCR_PENDING"))

    # Migrate data if any exists: raw_text -> extracted_text, structured_data -> bounding_boxes, confidence_score -> average_confidence, etc.
    op.execute("UPDATE ocr_results SET extracted_text = raw_text, bounding_boxes = structured_data, average_confidence = COALESCE(confidence_score, 0.0), processing_time = COALESCE(processing_time_ms, 0) / 1000.0, ocr_engine_version = COALESCE(engine_version, 'unknown'), preprocessing_version = 'unknown', original_image_path = '', processed_image_path = '', status = 'OCR_COMPLETED'")

    # Alter columns to be non-nullable after migration
    op.alter_column("ocr_results", "extracted_text", nullable=False)
    op.alter_column("ocr_results", "bounding_boxes", nullable=False)
    op.alter_column("ocr_results", "average_confidence", nullable=False, server_default="0.0")
    op.alter_column("ocr_results", "processing_time", nullable=False, server_default="0.0")
    op.alter_column("ocr_results", "ocr_engine_version", nullable=False, server_default="unknown")
    op.alter_column("ocr_results", "preprocessing_version", nullable=False, server_default="unknown")
    op.alter_column("ocr_results", "original_image_path", nullable=False, server_default="")
    op.alter_column("ocr_results", "processed_image_path", nullable=False, server_default="")

    # We also change confidence_score to not nullable, but we'll default it to 0.0
    op.execute("UPDATE ocr_results SET confidence_score = 0.0 WHERE confidence_score IS NULL")
    op.alter_column("ocr_results", "confidence_score", nullable=False, server_default="0.0")

    # Remove server defaults from columns where they shouldn't persist
    op.alter_column("ocr_results", "page_number", server_default=None)

    # 3. Drop old columns
    op.drop_column("ocr_results", "raw_text")
    op.drop_column("ocr_results", "structured_data")
    op.drop_column("ocr_results", "processing_time_ms")
    op.drop_column("ocr_results", "engine_version")

    # 4. Create composite unique constraint and indexes
    op.create_unique_constraint("uq_ocr_results_sheet_page", "ocr_results", ["answer_sheet_id", "page_number"])
    op.create_index("ix_ocr_results_answer_sheet_id", "ocr_results", ["answer_sheet_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ocr_results_answer_sheet_id", table_name="ocr_results")
    op.drop_constraint("uq_ocr_results_sheet_page", "ocr_results", type_="unique")

    op.add_column("ocr_results", sa.Column("raw_text", sa.Text(), nullable=True))
    op.add_column("ocr_results", sa.Column("structured_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("ocr_results", sa.Column("processing_time_ms", sa.Integer(), nullable=True))
    op.add_column("ocr_results", sa.Column("engine_version", sa.String(length=50), nullable=True))

    op.execute("UPDATE ocr_results SET raw_text = extracted_text, structured_data = bounding_boxes, processing_time_ms = CAST(processing_time * 1000 AS INTEGER), engine_version = ocr_engine_version")

    op.alter_column("ocr_results", "raw_text", nullable=False)
    op.alter_column("ocr_results", "structured_data", nullable=False)

    op.drop_column("ocr_results", "status")
    op.drop_column("ocr_results", "processed_image_path")
    op.drop_column("ocr_results", "original_image_path")
    op.drop_column("ocr_results", "preprocessing_version")
    op.drop_column("ocr_results", "ocr_engine_version")
    op.drop_column("ocr_results", "processing_time")
    op.drop_column("ocr_results", "words_detected")
    op.drop_column("ocr_results", "average_confidence")
    op.drop_column("ocr_results", "low_confidence_flag")
    op.drop_column("ocr_results", "bounding_boxes")
    op.drop_column("ocr_results", "extracted_text")
    op.drop_column("ocr_results", "page_number")

    op.alter_column("ocr_results", "confidence_score", nullable=True, server_default=None)

    op.create_unique_constraint("ocr_results_answer_sheet_id_key", "ocr_results", ["answer_sheet_id"])
