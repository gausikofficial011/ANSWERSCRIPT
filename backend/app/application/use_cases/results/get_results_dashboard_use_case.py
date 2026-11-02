"""
application/use_cases/results/get_results_dashboard_use_case.py — Get Results Dashboard Use Case
"""

from __future__ import annotations
import logging
from sqlalchemy import select, func

from app.domain.repositories.final_result_repository import FinalResultRepository
from app.infrastructure.persistence.models.final_result_model import FinalResultModel
from app.core.constants import PassFailStatus

logger = logging.getLogger(__name__)


class GetResultsDashboardUseCase:
    """
    Computes aggregated performance indicators across all exam submissions.
    """

    def __init__(self, final_result_repo: FinalResultRepository) -> None:
        self.final_result_repo = final_result_repo

    async def execute(self) -> dict:
        """
        Calculates total evaluated students, pass/fail splits, average score, and publication statistics.
        """
        # If the repository is SQLAlchemy-based, perform aggregate queries
        if hasattr(self.final_result_repo, "session"):
            session = self.final_result_repo.session

            # 1. Total results count
            count_query = select(func.count(FinalResultModel.id))
            count_result = await session.execute(count_query)
            total_results = count_result.scalar() or 0

            # 2. Total published results count
            pub_query = select(func.count(FinalResultModel.id)).where(FinalResultModel.is_published.is_(True))
            pub_result = await session.execute(pub_query)
            total_published = pub_result.scalar() or 0

            # 3. Average score (percentage)
            avg_query = select(func.avg(FinalResultModel.percentage))
            avg_result = await session.execute(avg_query)
            avg_score = float(avg_result.scalar() or 0.0)

            # 4. Pass count
            pass_query = select(func.count(FinalResultModel.id)).where(FinalResultModel.pass_fail_status == PassFailStatus.PASS.value)
            pass_result = await session.execute(pass_query)
            pass_count = pass_result.scalar() or 0

        else:
            # Fallback for in-memory repositories / mocks
            all_results = await self.final_result_repo.get_all() if hasattr(self.final_result_repo, "get_all") else []
            total_results = len(all_results)
            total_published = sum(1 for r in all_results if r.is_published)
            avg_score = (sum(r.percentage for r in all_results) / total_results) if total_results > 0 else 0.0
            pass_count = sum(1 for r in all_results if r.pass_fail_status == PassFailStatus.PASS or r.pass_fail_status == PassFailStatus.PASS.value)

        pending_publication = total_results - total_published
        
        pass_rate = (pass_count / total_results) * 100.0 if total_results > 0 else 0.0
        fail_rate = 100.0 - pass_rate if total_results > 0 else 0.0

        return {
            "total_students_evaluated": total_results,
            "total_results": total_results,
            "total_published": total_published,
            "pending_publication": pending_publication,
            "average_score": avg_score,
            "pass_rate": pass_rate,
            "fail_rate": fail_rate
        }
