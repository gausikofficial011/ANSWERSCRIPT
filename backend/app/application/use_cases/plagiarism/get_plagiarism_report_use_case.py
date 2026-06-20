"""
application/use_cases/plagiarism/get_plagiarism_report_use_case.py — Get Plagiarism Report Use Case
"""

from __future__ import annotations

import logging
import uuid
from typing import List

from app.domain.entities.plagiarism_report import PlagiarismReport
from app.domain.entities.plagiarism_similarity import PlagiarismSimilarity
from app.domain.repositories.plagiarism_repository import PlagiarismRepository
from app.domain.repositories.plagiarism_similarity_repository import PlagiarismSimilarityRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.exceptions.domain_exception import EntityNotFoundException

logger = logging.getLogger(__name__)


class GetPlagiarismReportUseCase:
    """
    Retrieves plagiarism reports and similarities details.
    """

    def __init__(
        self,
        plagiarism_repo: PlagiarismRepository,
        plagiarism_similarity_repo: PlagiarismSimilarityRepository,
        answer_sheet_repo: AnswerSheetRepository | None = None
    ) -> None:
        self.plagiarism_repo = plagiarism_repo
        self.plagiarism_similarity_repo = plagiarism_similarity_repo
        self.answer_sheet_repo = answer_sheet_repo

    async def get_exam_summary(self, exam_id: uuid.UUID) -> dict:
        """
        Calculates plagiarism statistics and top flagged student pairs for an exam.
        """
        reports = await self.get_by_exam_id(exam_id)
        
        total_reports = len(reports)
        high_risk_count = sum(1 for r in reports if r.risk_level == "HIGH_RISK")
        suspicious_count = sum(1 for r in reports if r.risk_level == "SUSPICIOUS")
        clean_count = sum(1 for r in reports if r.risk_level == "CLEAN")
        
        highest_sim = max((r.highest_similarity for r in reports), default=0.0)
        avg_sim = (sum(r.similarity_percentage for r in reports) / total_reports) if total_reports > 0 else 0.0
        
        flagged_sheets_count = 0
        if self.answer_sheet_repo:
            sheets = await self.answer_sheet_repo.get_all_by_exam_id(exam_id)
            flagged_sheets_count = sum(1 for s in sheets if s.plagiarism_flagged)
        
        # Sort reports by highest similarity desc and take top 5
        top_flagged_pairs = []
        sorted_reports = sorted(reports, key=lambda r: r.highest_similarity, reverse=True)
        for r in sorted_reports[:5]:
            top_flagged_pairs.append({
                "report_id": str(r.id),
                "source_answer_sheet_id": str(r.source_answer_sheet_id),
                "target_answer_sheet_id": str(r.target_answer_sheet_id),
                "similarity_percentage": r.similarity_percentage,
                "highest_similarity": r.highest_similarity,
                "risk_level": r.risk_level,
                "status": r.status.value if hasattr(r.status, "value") else str(r.status)
            })
            
        return {
            "exam_id": str(exam_id),
            "total_reports": total_reports,
            "high_risk_count": high_risk_count,
            "suspicious_count": suspicious_count,
            "clean_count": clean_count,
            "highest_similarity": highest_sim,
            "average_similarity": avg_sim,
            "flagged_sheets_count": flagged_sheets_count,
            "top_flagged_pairs": top_flagged_pairs
        }

    async def get_by_id(self, report_id: uuid.UUID) -> PlagiarismReport:
        """
        Fetch a report by ID.
        """
        report = await self.plagiarism_repo.get_by_id(report_id)
        if not report:
            raise EntityNotFoundException(entity_type="PlagiarismReport", entity_id=report_id)
        return report

    async def get_by_answer_sheet_id(self, answer_sheet_id: uuid.UUID) -> list[PlagiarismReport]:
        """
        Fetch reports involving a specific answer sheet.
        """
        return await self.plagiarism_repo.get_sheet_similarity_reports(answer_sheet_id)

    async def get_by_exam_id(self, exam_id: uuid.UUID) -> list[PlagiarismReport]:
        """
        Fetch all reports for an exam.
        """
        return await self.plagiarism_repo.get_by_exam_id(exam_id)

    async def get_similarities(self, report_id: uuid.UUID) -> list[PlagiarismSimilarity]:
        """
        Fetch all question-level similarities for a report.
        """
        report = await self.get_by_id(report_id)
        return await self.plagiarism_similarity_repo.list_by_pair(
            report.source_answer_sheet_id,
            report.target_answer_sheet_id
        )

    async def list_all_reports(self) -> list[PlagiarismReport]:
        """
        Fetch all plagiarism reports in the database (or up to a sensible limit).
        """
        # Since BaseRepository doesn't expose a simple get_all without PaginationParams,
        # we can query through the session, or retrieve by listing.
        # Let's check if plagiarism_repo has get_all or list.
        # If we need a simple implementation, we can list reports, or retrieve via custom query.
        # But wait! We can just fetch via list_reports with a select on model_class or similar.
        # Let's look at get_sheet_similarity_reports or similar.
        # To keep it generic and safe, we can implement list_all_reports:
        # Since SqlPlagiarismRepository inherits from SqlBaseRepository, it has access to self.session.
        # So we can execute select.
        from sqlalchemy import select
        from app.infrastructure.persistence.models.plagiarism_report_model import PlagiarismReportModel
        
        # We can cast or access the session directly if it's SqlPlagiarismRepository
        if hasattr(self.plagiarism_repo, "session"):
            query = select(PlagiarismReportModel)
            result = await self.plagiarism_repo.session.execute(query)
            models = result.scalars().all()
            return [self.plagiarism_repo.to_entity(m) for m in models]
        return []
