"""
application/use_cases/results/generate_exam_report_pdf_use_case.py — Generate Exam Report PDF Use Case
"""

from __future__ import annotations
import uuid
from datetime import datetime

from app.application.use_cases.results.get_exam_results_use_case import GetExamResultsUseCase
from app.infrastructure.reports.weasyprint_pdf_service import WeasyPrintPDFService
from app.domain.repositories.exam_repository import ExamRepository
from app.domain.repositories.subject_repository import SubjectRepository


class GenerateExamReportPDFUseCase:
    """
    Use Case: Fetches all candidate scores for an exam, performs statistics calculations,
    resolves subject metadata, and compiles them to PDF bytes in memory.
    """

    def __init__(
        self,
        get_exam_results_use_case: GetExamResultsUseCase,
        exam_repo: ExamRepository,
        subject_repo: SubjectRepository,
        pdf_service: WeasyPrintPDFService
    ) -> None:
        self.get_exam_results_use_case = get_exam_results_use_case
        self.exam_repo = exam_repo
        self.subject_repo = subject_repo
        self.pdf_service = pdf_service

    async def execute(self, exam_id: uuid.UUID) -> bytes:
        # 1. Fetch exam results from use case
        data = await self.get_exam_results_use_case.execute(
            exam_id=exam_id,
            page=1,
            page_size=1000000
        )

        items = data.get("items", [])
        total_candidates = len(items)

        # 2. Compute diagnostics
        if total_candidates > 0:
            percentages = [item.get("percentage", 0.0) for item in items]
            average_percentage = sum(percentages) / total_candidates
            
            pass_count = sum(1 for item in items if item.get("pass_fail_status", "").upper() == "PASS")
            pass_rate = (pass_count / total_candidates) * 100.0
            fail_rate = 100.0 - pass_rate
        else:
            average_percentage = 0.0
            pass_rate = 0.0
            fail_rate = 0.0

        # 3. Resolve Subject Name
        subject_name = "General"
        exam = await self.exam_repo.get_by_id(exam_id)
        if exam:
            subject = await self.subject_repo.get_by_id(exam.subject_id)
            if subject:
                subject_name = f"{subject.name} ({subject.code})"

        # 4. Construct context
        context = {
            "exam_title": data.get("exam_title", ""),
            "exam_id": str(exam_id),
            "subject_name": subject_name,
            "total_marks": data.get("total_marks", 0),
            "passing_marks": data.get("passing_marks", 0),
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "total_candidates": total_candidates,
            "average_percentage": average_percentage,
            "pass_rate": pass_rate,
            "fail_rate": fail_rate,
            "items": items,
            "verification_id": str(uuid.uuid4())
        }

        # 5. Compile PDF
        return self.pdf_service.generate_pdf("exam_report.html", context)
