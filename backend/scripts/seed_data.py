"""
backend/scripts/seed_data.py — Database Seeder Script

Seeds the database with default roles, a default admin, a default teacher,
and sample academic data (subjects, exams, questions, rubrics).
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.database import AsyncSessionLocal
from app.infrastructure.persistence.models import (
    RoleModel,
    UserModel,
    TeacherModel,
    StudentModel,
    SubjectModel,
    ExamModel,
    QuestionModel,
    ModelAnswerModel,
    RubricModel,
    RubricCriterionModel,
)
from app.core.constants import ExamStatus, QuestionType, GradingMode

# Pre-hashed password for "password123" (bcrypt work factor 12)
DEFAULT_HASHED_PASSWORD = "$2b$12$EixZaYVK1YiYi1x17Ryod.n0H5GQ2M74J4R4q8R4QzY0.4fW6q.K6"


async def seed_database(session: AsyncSession) -> None:
    print("Starting database seeding...")

    # 1. Seed Roles
    admin_role_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    teacher_role_id = uuid.UUID("22222222-2222-2222-2222-222222222222")

    admin_role = RoleModel(
        id=admin_role_id,
        name="admin",
        description="System Administrator with full access"
    )
    teacher_role = RoleModel(
        id=teacher_role_id,
        name="teacher",
        description="Teacher/Evaluator with access to subjects and exams"
    )

    session.add_all([admin_role, teacher_role])
    await session.flush()
    print("✓ Seeding roles completed.")

    # 2. Seed Users
    admin_user_id = uuid.UUID("33333333-3333-3333-3333-333333333333")
    teacher_user_id = uuid.UUID("44444444-4444-4444-4444-444444444444")

    admin_user = UserModel(
        id=admin_user_id,
        email="admin@amaes.edu",
        username="admin",
        hashed_password=DEFAULT_HASHED_PASSWORD,
        full_name="System Administrator",
        role_id=admin_role_id,
        is_active=True,
        is_verified=True
    )
    teacher_user = UserModel(
        id=teacher_user_id,
        email="teacher@amaes.edu",
        username="teacher",
        hashed_password=DEFAULT_HASHED_PASSWORD,
        full_name="Dr. Jane Smith",
        role_id=teacher_role_id,
        is_active=True,
        is_verified=True
    )

    session.add_all([admin_user, teacher_user])
    await session.flush()

    # Create associated teacher profile
    teacher_profile_id = uuid.UUID("55555555-5555-5555-5555-555555555555")
    teacher_profile = TeacherModel(
        id=teacher_profile_id,
        user_id=teacher_user_id,
        department="Computer Science",
        employee_code="CS-101"
    )
    session.add(teacher_profile)
    await session.flush()
    print("✓ Seeding users and teacher profiles completed.")

    # 3. Seed Students
    student_1 = StudentModel(
        id=uuid.UUID("a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"),
        student_number="STU-001",
        full_name="Alice Vance",
        email="alice@student.amaes.edu",
        class_section="CS-A"
    )
    student_2 = StudentModel(
        id=uuid.UUID("b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2"),
        student_number="STU-002",
        full_name="Bob Miller",
        email="bob@student.amaes.edu",
        class_section="CS-A"
    )
    session.add_all([student_1, student_2])
    await session.flush()
    print("✓ Seeding students completed.")

    # 4. Seed Subjects
    subject_id = uuid.UUID("66666666-6666-6666-6666-666666666666")
    subject = SubjectModel(
        id=subject_id,
        name="Data Structures and Algorithms",
        code="CS202",
        description="Core computer science course covering stacks, queues, trees, and graphs.",
        language="en",
        created_by=teacher_user_id,
        is_active=True
    )
    session.add(subject)
    await session.flush()
    print("✓ Seeding subjects completed.")

    # 5. Seed Exam
    exam_id = uuid.UUID("77777777-7777-7777-7777-777777777777")
    exam = ExamModel(
        id=exam_id,
        subject_id=subject_id,
        title="Midterm Examination - CS202",
        description="Midterm test covering Stack and Queue structures.",
        exam_date=date(2026, 6, 20),
        total_marks=20,
        passing_marks=10,
        duration_minutes=60,
        status=ExamStatus.ACTIVE,
        scoring_config={
            "semantic_weight": 0.6,
            "keyword_weight": 0.4,
            "plagiarism_threshold": 0.85
        },
        created_by=teacher_user_id
    )
    session.add(exam)
    await session.flush()
    print("✓ Seeding exams completed.")

    # 6. Seed Question & Model Answer
    question_id = uuid.UUID("88888888-8888-8888-8888-888888888888")
    question = QuestionModel(
        id=question_id,
        exam_id=exam_id,
        question_number=1,
        question_text="Explain the difference between a Stack and a Queue data structure.",
        marks=10,
        question_type=QuestionType.SHORT,
        language="en",
        created_by=teacher_user_id
    )
    session.add(question)
    await session.flush()

    model_answer = ModelAnswerModel(
        id=uuid.UUID("99999999-9999-9999-9999-999999999999"),
        question_id=question_id,
        answer_text="A Stack is a Last-In-First-Out (LIFO) data structure where elements are inserted and removed from the same end, called the top. A Queue is a First-In-First-Out (FIFO) data structure where elements are inserted at the rear (enqueue) and removed from the front (dequeue).",
        keywords=["Stack", "Queue", "LIFO", "FIFO", "Last-In-First-Out", "First-In-First-Out", "top", "rear", "front"],
        created_by=teacher_user_id
    )
    session.add(model_answer)
    await session.flush()
    print("✓ Seeding questions and model answers completed.")

    # 7. Seed Rubrics & Rubric Criteria
    rubric_id = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    rubric = RubricModel(
        id=rubric_id,
        question_id=question_id,
        title="Stack vs Queue Grading Rubric",
        description="Standard evaluation rubric to check definition correctness and terminology mapping.",
        total_weight=1.0,
        version=1,
        is_active=True,
        grading_mode=GradingMode.HYBRID,
        created_by=teacher_user_id
    )
    session.add(rubric)
    await session.flush()

    criterion_1 = RubricCriterionModel(
        id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        rubric_id=rubric_id,
        criterion_name="Stack Definition",
        criterion_description="Accurate explanation of Stack LIFO behavior and operations.",
        weight=0.5,
        max_marks=5.0,
        expected_keywords=["Stack", "LIFO", "Last-In-First-Out", "top"],
        order_index=0
    )
    criterion_2 = RubricCriterionModel(
        id=uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        rubric_id=rubric_id,
        criterion_name="Queue Definition",
        criterion_description="Accurate explanation of Queue FIFO behavior and enqueue/dequeue operations.",
        weight=0.5,
        max_marks=5.0,
        expected_keywords=["Queue", "FIFO", "First-In-First-Out", "rear", "front"],
        order_index=1
    )
    session.add_all([criterion_1, criterion_2])
    await session.flush()
    print("✓ Seeding rubrics and rubric criteria completed.")

    print("Seeding database completed successfully!")


async def main() -> None:
    async with AsyncSessionLocal() as session:
        try:
            await seed_database(session)
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Error during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
