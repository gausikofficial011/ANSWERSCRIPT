"""
tests/unit/application/test_export_use_cases.py — Unit Tests for Export CSV Use Cases
"""

from __future__ import annotations
import csv
import io
import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.application.use_cases.results.export_exam_results_csv_use_case import ExportExamResultsCSVUseCase
from app.application.use_cases.results.export_student_results_csv_use_case import ExportStudentResultsCSVUseCase
from app.application.use_cases.results.get_exam_results_use_case import GetExamResultsUseCase
from app.application.use_cases.results.get_student_results_use_case import GetStudentResultsUseCase


@pytest.mark.asyncio
async def test_export_exam_results_csv_success():
    mock_get_exam = MagicMock(spec=GetExamResultsUseCase)
    mock_get_exam.execute = AsyncMock(return_value={
        "exam_id": str(uuid.uuid4()),
        "exam_title": "DSA Midterm",
        "total_marks": 100,
        "passing_marks": 40,
        "items": [
            {
                "student_id": uuid.uuid4(),
                "student_name": "Alice Vance",
                "student_number": "STU-001",
                "marks_obtained": 85.5,
                "percentage": 85.5,
                "grade": "A+",
                "pass_fail_status": "PASS",
                "verification_status": "VERIFIED",
                "publication_status": "PUBLISHED"
            },
            {
                "student_id": uuid.uuid4(),
                "student_name": "Bob, the Builder",  # Special character: comma
                "student_number": "STU-002",
                "marks_obtained": 35.0,
                "percentage": 35.0,
                "grade": "F",
                "pass_fail_status": "FAIL",
                "verification_status": "VERIFIED",
                "publication_status": "UNPUBLISHED"
            },
            {
                "student_id": uuid.uuid4(),
                "student_name": "Müller UTF8",  # Special character: umlaut
                "student_number": "STU-003",
                "marks_obtained": 90.0,
                "percentage": 90.0,
                "grade": "O",
                "pass_fail_status": "PASS",
                "verification_status": "VERIFIED",
                "publication_status": "PUBLISHED"
            }
        ]
    })

    use_case = ExportExamResultsCSVUseCase(mock_get_exam)
    exam_id = uuid.uuid4()
    csv_data = await use_case.execute(exam_id)

    mock_get_exam.execute.assert_called_once_with(exam_id=exam_id, page=1, page_size=1000000)

    reader = csv.reader(io.StringIO(csv_data))
    rows = list(reader)

    # Header check
    assert rows[0] == [
        "Student Number",
        "Student Name",
        "Marks Obtained",
        "Total Marks",
        "Percentage",
        "Grade",
        "Pass/Fail Status",
        "Verification Status",
        "Publication Status"
    ]

    # Row checks
    assert len(rows) == 4
    assert rows[1] == ["STU-001", "Alice Vance", "85.5", "100", "85.5", "A+", "PASS", "VERIFIED", "PUBLISHED"]
    assert rows[2] == ["STU-002", "Bob, the Builder", "35.0", "100", "35.0", "F", "FAIL", "VERIFIED", "UNPUBLISHED"]
    assert rows[3] == ["STU-003", "Müller UTF8", "90.0", "100", "90.0", "O", "PASS", "VERIFIED", "PUBLISHED"]


@pytest.mark.asyncio
async def test_export_exam_results_csv_empty():
    mock_get_exam = MagicMock(spec=GetExamResultsUseCase)
    mock_get_exam.execute = AsyncMock(return_value={
        "exam_id": str(uuid.uuid4()),
        "exam_title": "DSA Midterm",
        "total_marks": 100,
        "passing_marks": 40,
        "items": []
    })

    use_case = ExportExamResultsCSVUseCase(mock_get_exam)
    csv_data = await use_case.execute(uuid.uuid4())

    reader = csv.reader(io.StringIO(csv_data))
    rows = list(reader)

    assert len(rows) == 1
    assert rows[0][0] == "Student Number"


@pytest.mark.asyncio
async def test_export_student_results_csv_success():
    mock_get_student = MagicMock(spec=GetStudentResultsUseCase)
    mock_get_student.execute = AsyncMock(return_value={
        "student_id": str(uuid.uuid4()),
        "student_name": "Alice Vance",
        "student_number": "STU-001",
        "class_section": "A",
        "history": [
            {
                "exam_id": uuid.uuid4(),
                "exam_title": "DSA Midterm",
                "subject_name": "Data Structures, Algorithms",
                "percentage": 85.5,
                "grade": "A+",
                "pass_fail_status": "PASS",
                "published_status": "PUBLISHED"
            },
            {
                "exam_id": uuid.uuid4(),
                "exam_title": "OS Final",
                "subject_name": "Operating Systems",
                "percentage": 92.0,
                "grade": "O",
                "pass_fail_status": "PASS",
                "published_status": "PUBLISHED"
            }
        ]
    })

    use_case = ExportStudentResultsCSVUseCase(mock_get_student)
    student_id = uuid.uuid4()
    csv_data = await use_case.execute(student_id)

    mock_get_student.execute.assert_called_once_with(student_id=student_id)

    reader = csv.reader(io.StringIO(csv_data))
    rows = list(reader)

    assert rows[0] == [
        "Subject Name",
        "Exam Title",
        "Percentage",
        "Grade",
        "Pass/Fail Status",
        "Publication Status"
    ]

    assert len(rows) == 3
    assert rows[1] == ["Data Structures, Algorithms", "DSA Midterm", "85.5", "A+", "PASS", "PUBLISHED"]
    assert rows[2] == ["Operating Systems", "OS Final", "92.0", "O", "PASS", "PUBLISHED"]


@pytest.mark.asyncio
async def test_export_student_results_csv_empty():
    mock_get_student = MagicMock(spec=GetStudentResultsUseCase)
    mock_get_student.execute = AsyncMock(return_value={
        "student_id": str(uuid.uuid4()),
        "student_name": "Alice Vance",
        "student_number": "STU-001",
        "class_section": "A",
        "history": []
    })

    use_case = ExportStudentResultsCSVUseCase(mock_get_student)
    csv_data = await use_case.execute(uuid.uuid4())

    reader = csv.reader(io.StringIO(csv_data))
    rows = list(reader)

    assert len(rows) == 1
    assert rows[0][0] == "Subject Name"
