"""
infrastructure/ai/plagiarism_score_service.py — Plagiarism Score Aggregation Service
"""

from __future__ import annotations

from app.infrastructure.ai.semantic_plagiarism_service import SemanticPlagiarismService
from app.infrastructure.ai.lexical_similarity_service import LexicalSimilarityService
from app.infrastructure.ai.overlap_detection_service import OverlapDetectionService


class PlagiarismScoreService:
    """
    Combines semantic (50%), lexical (30%), and exact overlap (20%) similarity scores.
    """

    def __init__(
        self,
        semantic_service: SemanticPlagiarismService | None = None,
        lexical_service: LexicalSimilarityService | None = None,
        overlap_service: OverlapDetectionService | None = None
    ) -> None:
        self.semantic_service = semantic_service or SemanticPlagiarismService()
        self.lexical_service = lexical_service or LexicalSimilarityService()
        self.overlap_service = overlap_service or OverlapDetectionService()

    def compute_scores(
        self,
        text1: str,
        text2: str,
        embedding1: list[float] | None = None,
        embedding2: list[float] | None = None
    ) -> dict[str, float]:
        """
        Calculates individual similarities and the weighted final similarity score.
        """
        if not text1.strip() or not text2.strip():
            return {
                "semantic": 0.0,
                "lexical": 0.0,
                "overlap": 0.0,
                "final": 0.0
            }

        sem = self.semantic_service.compute_similarity(text1, text2, embedding1, embedding2)
        lex = self.lexical_service.compute_similarity(text1, text2)
        ovl = self.overlap_service.compute_similarity(text1, text2)

        # 50% semantic similarity + 30% lexical similarity + 20% exact overlap match
        final_score = 0.5 * sem + 0.3 * lex + 0.2 * ovl
        final_score = min(1.0, max(0.0, final_score))

        return {
            "semantic": float(sem),
            "lexical": float(lex),
            "overlap": float(ovl),
            "final": float(final_score)
        }

    def get_embedding(self, text: str) -> list[float]:
        return self.semantic_service.get_embedding(text)
