"""
application/use_cases/results/export_student_results_csv_use_case.py — Export Student Results as CSV
"""

from __future__ import annotations
import csv
import io
import uuid

from app.application.use_cases.results.get_student_results_use_case import GetStudentResultsUseCase


class ExportStudentResultsCSVUseCase:
    """
    Export Layer: Formats student academic history record into a CSV payload.
    Reuses GetStudentResultsUseCase to avoid duplicating query or subject mappings.
    """

    def __init__(self, get_student_results_use_case: GetStudentResultsUseCase) -> None:
        self.get_student_results_use_case = get_student_results_use_case

    async def execute(self, student_id: uuid.UUID, only_published: bool = False) -> str:
        kwargs = {"student_id": student_id}
        if only_published:
            kwargs["only_published"] = True
        data = await self.get_student_results_use_case.execute(**kwargs)

        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\n')

        # CSV Headers
        writer.writerow([
            "Subject Name",
            "Exam Title",
            "Percentage",
            "Grade",
            "Pass/Fail Status",
            "Publication Status"
        ])

        history = data.get("history", [])

        for item in history:
            writer.writerow([
                item.get("subject_name", ""),
                item.get("exam_title", ""),
                f"{item.get('percentage', 0.0):.1f}",
                item.get("grade") or "",
                item.get("pass_fail_status", ""),
                item.get("published_status", "")
            ])

        return output.getvalue()
