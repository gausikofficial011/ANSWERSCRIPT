"""
app/api/v1/routers/academic.py — Academic Administration Endpoints

Manages departments, programs, student enrolment cohorts, and faculty assignments.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.models.subject_model import SubjectModel
from app.infrastructure.persistence.models.student_model import StudentModel

router = APIRouter(prefix="/academic", tags=["Academic Administration"])


@router.get("/departments", response_model=Dict[str, Any])
async def list_departments(db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Returns department and curriculum hierarchy."""
    subjects_res = await db.execute(select(SubjectModel))
    subjects = subjects_res.scalars().all()

    # Organized by academic department
    departments = [
        {
            "id": "dept-cs",
            "name": "Department of Computer Science & Engineering",
            "code": "CSE",
            "head": "Dr. Ramesh Babu, Ph.D.",
            "programs": [
                {
                    "name": "Master of Computer Applications (MCA)",
                    "code": "MCA-2025",
                    "semesters": 4,
                    "subjects_count": len(subjects)
                },
                {
                    "name": "B.Tech in Artificial Intelligence & Data Science",
                    "code": "BTECH-AIDS",
                    "semesters": 8,
                    "subjects_count": 8
                }
            ]
        },
        {
            "id": "dept-it",
            "name": "Department of Information Technology",
            "code": "IT",
            "head": "Dr. Ananya Sharma, Ph.D.",
            "programs": [
                {
                    "name": "M.Tech in Cyber Security & Forensic Intelligence",
                    "code": "MTECH-CYBER",
                    "semesters": 4,
                    "subjects_count": 6
                }
            ]
        }
    ]

    return {
        "total_departments": len(departments),
        "departments": departments,
        "active_subjects": [
            {"id": str(s.id), "name": s.name, "code": s.code} for s in subjects
        ]
    }


@router.get("/cohorts", response_model=Dict[str, Any])
async def list_cohorts(db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Returns active academic student cohorts."""
    students_res = await db.execute(select(StudentModel))
    students = students_res.scalars().all()

    return {
        "total_cohorts": 2,
        "cohorts": [
            {
                "id": "cohort-mca-2025-a",
                "name": "MCA 2024-2026 Batch — Section A",
                "program": "Master of Computer Applications",
                "semester": "Semester III",
                "enrolled_students": len(students),
                "faculty_advisor": "Prof. S. Narayanan",
                "status": "ACTIVE"
            },
            {
                "id": "cohort-btech-ai-2025",
                "name": "B.Tech AI&DS Batch 2023-2027",
                "program": "B.Tech AI & Data Science",
                "semester": "Semester V",
                "enrolled_students": 45,
                "faculty_advisor": "Dr. K. Meenakshi",
                "status": "ACTIVE"
            }
        ]
    }
