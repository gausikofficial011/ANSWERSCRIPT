"""
application/use_cases/results/generate_student_transcript_pdf_use_case.py — Generate Student Transcript PDF Use Case
"""

from __future__ import annotations
import uuid
from datetime import datetime

from app.application.use_cases.results.get_student_results_use_case import GetStudentResultsUseCase
from app.infrastructure.reports.weasyprint_pdf_service import WeasyPrintPDFService


class GenerateStudentTranscriptPDFUseCase:
    """
    Use Case: Fetches student results history, aggregates score percentages,
    and invokes the WeasyPrint PDF service to return in-memory PDF bytes.
    Does NOT calculate GPA, credit weights, or grade points.
    """

    def __init__(
        self,
        get_student_results_use_case: GetStudentResultsUseCase,
        pdf_service: WeasyPrintPDFService
    ) -> None:
        self.get_student_results_use_case = get_student_results_use_case
        self.pdf_service = pdf_service

    async def execute(self, student_id: uuid.UUID, only_published: bool = True) -> bytes:
        # 1. Fetch student history profile
        data = await self.get_student_results_use_case.execute(student_id, only_published=only_published)
        
        # 2. Extract and filter to PUBLISHED items for transcript
        history = data.get("history", [])
        if only_published:
            published_history = [item for item in history if item.get("published_status") == "PUBLISHED"]
        else:
            published_history = history
        
        total_exams = len(published_history)
        
        if total_exams > 0:
            percentages = [item.get("percentage", 0.0) for item in published_history]
            average_percentage = sum(percentages) / total_exams
            highest_percentage = max(percentages)
            lowest_percentage = min(percentages)
            
            pass_count = sum(1 for item in published_history if item.get("pass_fail_status", "").upper() == "PASS")
            pass_rate = (pass_count / total_exams) * 100.0
        else:
            average_percentage = 0.0
            highest_percentage = 0.0
            lowest_percentage = 0.0
            pass_rate = 0.0

        # 3. Construct Jinja context matching HTML parameters
        context = {
            "student_name": data.get("student_name", ""),
            "student_number": data.get("student_number", ""),
            "class_section": data.get("class_section"),
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "total_exams": total_exams,
            "average_percentage": average_percentage,
            "highest_percentage": highest_percentage,
            "lowest_percentage": lowest_percentage,
            "pass_rate": pass_rate,
            "history": published_history,
            "verification_id": str(uuid.uuid4())
        }

        # 4. Generate PDF bytes
        return self.pdf_service.generate_pdf("transcript.html", context)
