"""
application/use_cases/results/export_exam_results_csv_use_case.py — Export Exam Results as CSV
"""

from __future__ import annotations
import csv
import io
import uuid

from app.application.use_cases.results.get_exam_results_use_case import GetExamResultsUseCase


class ExportExamResultsCSVUseCase:
    """
    Export Layer: Formats all results of an exam into a CSV payload.
    Reuses GetExamResultsUseCase to avoid duplicating aggregation/sync logic.
    """

    def __init__(self, get_exam_results_use_case: GetExamResultsUseCase) -> None:
        self.get_exam_results_use_case = get_exam_results_use_case

    async def execute(self, exam_id: uuid.UUID) -> str:
        # Fetch all results by requesting a very large page size
        data = await self.get_exam_results_use_case.execute(
            exam_id=exam_id,
            page=1,
            page_size=1000000
        )

        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\n')

        # CSV Headers
        writer.writerow([
            "Student Number",
            "Student Name",
            "Marks Obtained",
            "Total Marks",
            "Percentage",
            "Grade",
            "Pass/Fail Status",
            "Verification Status",
            "Publication Status"
        ])

        total_marks = data.get("total_marks", 0)
        items = data.get("items", [])

        for item in items:
            writer.writerow([
                item.get("student_number", ""),
                item.get("student_name", ""),
                item.get("marks_obtained", 0.0),
                total_marks,
                f"{item.get('percentage', 0.0):.1f}",
                item.get("grade") or "",
                item.get("pass_fail_status", ""),
                item.get("verification_status", ""),
                item.get("publication_status", "")
            ])

        return output.getvalue()
