"""
domain/entities/plagiarism_similarity.py — PlagiarismSimilarity Domain Entity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class PlagiarismSimilarity:
    """
    Represents a question-level plagiarism similarity check.
    """
    source_answer_sheet_id: uuid.UUID
    target_answer_sheet_id: uuid.UUID
    source_question_mapping_id: uuid.UUID
    target_question_mapping_id: uuid.UUID
    semantic_similarity: float
    lexical_similarity: float
    overlap_similarity: float
    final_similarity: float
    risk_level: str  # 'CLEAN', 'SUSPICIOUS', 'HIGH_RISK'
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        source_answer_sheet_id: uuid.UUID,
        target_answer_sheet_id: uuid.UUID,
        source_question_mapping_id: uuid.UUID,
        target_question_mapping_id: uuid.UUID,
        semantic_similarity: float,
        lexical_similarity: float,
        overlap_similarity: float,
        final_similarity: float,
        risk_level: str
    ) -> "PlagiarismSimilarity":
        return cls(
            source_answer_sheet_id=source_answer_sheet_id,
            target_answer_sheet_id=target_answer_sheet_id,
            source_question_mapping_id=source_question_mapping_id,
            target_question_mapping_id=target_question_mapping_id,
            semantic_similarity=semantic_similarity,
            lexical_similarity=lexical_similarity,
            overlap_similarity=overlap_similarity,
            final_similarity=final_similarity,
            risk_level=risk_level,
            id=uuid.uuid4(),
            created_at=datetime.now()
        )
