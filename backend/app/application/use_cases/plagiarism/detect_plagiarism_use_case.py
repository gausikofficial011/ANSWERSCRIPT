"""
application/use_cases/plagiarism/detect_plagiarism_use_case.py — Detect Plagiarism Use Case (Exam-wide)
"""

from __future__ import annotations

import logging
import uuid
from typing import List

from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.plagiarism_repository import PlagiarismRepository
from app.domain.repositories.plagiarism_similarity_repository import PlagiarismSimilarityRepository
from app.application.use_cases.plagiarism.detect_answer_sheet_plagiarism_use_case import DetectAnswerSheetPlagiarismUseCase
from app.domain.exceptions.domain_exception import EntityNotFoundException

logger = logging.getLogger(__name__)


class DetectPlagiarismUseCase:
    """
    Coordinates and executes plagiarism checks for all answer sheets in a specific exam.
    """

    def __init__(
        self,
        answer_sheet_repo: AnswerSheetRepository,
        plagiarism_repo: PlagiarismRepository,
        plagiarism_similarity_repo: PlagiarismSimilarityRepository,
        detect_sheet_use_case: DetectAnswerSheetPlagiarismUseCase
    ) -> None:
        self.answer_sheet_repo = answer_sheet_repo
        self.plagiarism_repo = plagiarism_repo
        self.plagiarism_similarity_repo = plagiarism_similarity_repo
        self.detect_sheet_use_case = detect_sheet_use_case

    async def execute(self, exam_id: uuid.UUID, user_id: uuid.UUID | None = None) -> dict:
        """
        Runs plagiarism checks exam-wide.
        Deletes old reports for the exam first, then scans sheet-by-sheet.
        """
        # 1. Clean up existing plagiarism data for the exam first
        # Delete similarities matching any sheet in the exam
        sheets = await self.answer_sheet_repo.get_all_by_exam_id(exam_id)
        if not sheets:
            return {
                "exam_id": str(exam_id),
                "total_sheets": 0,
                "scanned_sheets": 0,
                "status": "NO_SHEETS"
            }

        # Clear similarities for all sheets
        for sheet in sheets:
            await self.plagiarism_similarity_repo.delete_by_answer_sheet_id(sheet.id)

        # Clear reports for this exam
        await self.plagiarism_repo.delete_by_exam_id(exam_id)

        scanned_count = 0
        reports_count = 0
        highest_sim = 0.0
        processed_pairs: set[tuple[uuid.UUID, uuid.UUID]] = set()

        # 2. Run detection for each sheet
        # Since detect_sheet_use_case scans sheet-by-sheet and prevents self-comparisons,
        # we can scan each sheet sequentially.
        for sheet in sheets:
            result = await self.detect_sheet_use_case.execute(
                sheet.id,
                user_id=user_id,
                processed_pairs=processed_pairs
            )
            if result["status"] == "COMPLETED":
                scanned_count += 1
                reports_count += result["created_reports"]
                highest_sim = max(highest_sim, result["highest_similarity"])

        return {
            "exam_id": str(exam_id),
            "total_sheets": len(sheets),
            "scanned_sheets": scanned_count,
            "created_reports": reports_count,
            "highest_similarity": highest_sim,
            "status": "COMPLETED"
        }
