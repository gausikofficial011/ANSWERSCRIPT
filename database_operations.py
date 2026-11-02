"""
================================================================================
IntelliGrade Platform — Database Management & Operations Program
File: database_operations.py
Architecture: Clean Relational ORM (SQLAlchemy 2.0)
Compatible with: PostgreSQL (Production) & SQLite (Testing / Demonstration)
================================================================================
"""

import os
import sys
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    create_engine,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    select,
    func
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
    Session
)

# ── 1. CONFIGURATION & ENGINE SETUP ───────────────────────────────────────────
DB_FILE = "academic_evaluation.db"
# If running fresh, remove existing local SQLite db for a clean demonstration run
if os.path.exists(DB_FILE):
    try:
        os.remove(DB_FILE)
    except Exception:
        pass

DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# ── 2. DECLARATIVE BASE & ORM SCHEMAS ─────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class UserModel(Base):
    """Stores system actors (Admins, Teachers, Evaluators, Students)."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)  # admin, teacher, student
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<User({self.full_name}, Role: {self.role})>"


class ExamModel(Base):
    """Academic examinations associated with courses and semesters."""
    __tablename__ = "exams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    total_marks: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    questions: Mapped[List["QuestionModel"]] = relationship(back_populates="exam", cascade="all, delete-orphan")


class QuestionModel(Base):
    """Questions linked to an exam with maximum marks."""
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    max_marks: Mapped[float] = mapped_column(Float, nullable=False)

    exam: Mapped["ExamModel"] = relationship(back_populates="questions")
    rubric_criteria: Mapped[List["RubricCriterionModel"]] = relationship(back_populates="question")


class RubricCriterionModel(Base):
    """Multi-criterion grading rubrics (Semantic Weight Beta & Keywords)."""
    __tablename__ = "rubric_criteria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    criterion_name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_points: Mapped[float] = mapped_column(Float, nullable=False)
    semantic_weight: Mapped[float] = mapped_column(Float, default=0.65)  # Beta parameter

    question: Mapped["QuestionModel"] = relationship(back_populates="rubric_criteria")


class EvaluationModel(Base):
    """Stores AI scoring, teacher overrides, and publication status."""
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id"), nullable=False)
    ai_score: Mapped[float] = mapped_column(Float, nullable=False)
    teacher_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    final_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.90)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    ai_justification: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("student_id", "question_id", name="uq_student_question"),)


class AuditLogModel(Base):
    """Immutable audit trail for all score modifications and administrative actions."""
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_name: Mapped[str] = mapped_column(String(50), nullable=False)  # "evaluations"
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)       # "SCORE_OVERRIDE"
    performed_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[str] = mapped_column(Text, nullable=False)
    academic_rationale: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── 3. OPERATIONAL METHODS (BUSINESS LOGIC) ───────────────────────────────────

def init_database():
    """Initializes schema and tables."""
    print("[1/5] Initializing database schema and tables...")
    Base.metadata.create_all(bind=engine)
    print("      -> Successfully verified and created 6 relational tables:")
    print("         * users, exams, questions, rubric_criteria, evaluations, audit_logs")


def seed_master_data(session: Session):
    """Seeds foundational users, exams, and questions."""
    print("\n[2/5] Seeding master institutional records...")
    
    # Check if data already exists
    if session.scalars(select(UserModel)).first():
        print("      -> Master data already present. Skipping seed.")
        return

    # Seed Faculty & Students
    teacher = UserModel(
        id=str(uuid.uuid4()),
        email="prof.sharma@amaes.edu",
        full_name="Prof. Rajesh Sharma (Evaluator)",
        role="teacher"
    )
    student = UserModel(
        id=str(uuid.uuid4()),
        email="arjun.reddy@student.amaes.edu",
        full_name="Arjun Reddy (Roll: 24MCA01)",
        role="student"
    )
    session.add_all([teacher, student])
    session.flush()

    # Seed Exam & Question
    exam = ExamModel(
        id=str(uuid.uuid4()),
        code="CS-502",
        title="Advanced Database Systems & Transaction Processing",
        total_marks=100
    )
    session.add(exam)
    session.flush()

    q1 = QuestionModel(
        id=str(uuid.uuid4()),
        exam_id=exam.id,
        question_number=1,
        question_text="Explain ACID properties in relational DBMS transactions.",
        max_marks=10.0
    )
    session.add(q1)
    session.flush()

    # Seed Rubric Criteria (Atomicity, Consistency, Isolation, Durability)
    criteria = [
        RubricCriterionModel(question_id=q1.id, criterion_name="Atomicity & Rollback Mechanism", max_points=2.5, semantic_weight=0.65),
        RubricCriterionModel(question_id=q1.id, criterion_name="Consistency Invariants", max_points=2.5, semantic_weight=0.65),
        RubricCriterionModel(question_id=q1.id, criterion_name="Isolation & Concurrency Locks", max_points=2.5, semantic_weight=0.65),
        RubricCriterionModel(question_id=q1.id, criterion_name="Durability & WAL Logging", max_points=2.5, semantic_weight=0.65),
    ]
    session.add_all(criteria)
    session.commit()
    print("      -> Seeded: 1 Faculty, 1 Candidate Student, 1 Exam, 1 Question, 4 Rubric Criteria.")


def record_ai_evaluation(session: Session):
    """Simulates AI evaluation engine persisting a student score."""
    print("\n[3/5] Recording AI-proposed evaluation from OCR extraction...")
    
    student = session.scalars(select(UserModel).where(UserModel.role == "student")).first()
    question = session.scalars(select(QuestionModel)).first()

    existing_eval = session.scalars(
        select(EvaluationModel).where(
            EvaluationModel.student_id == student.id,
            EvaluationModel.question_id == question.id
        )
    ).first()

    if existing_eval:
        print("      -> AI Evaluation already recorded.")
        return existing_eval

    evaluation = EvaluationModel(
        id=str(uuid.uuid4()),
        student_id=student.id,
        question_id=question.id,
        ai_score=8.5,
        final_score=8.5,
        confidence=0.92,
        is_verified=False,
        ai_justification="Extracted answer accurately covers Atomicity, Consistency, and Isolation. Minor gap in Durability recovery example."
    )
    session.add(evaluation)
    session.commit()
    print(f"      -> AI Evaluation Stored: {evaluation.ai_score} / {question.max_marks} marks (Confidence: {evaluation.confidence * 100:.1f}%)")
    print(f"         AI Justification: \"{evaluation.ai_justification}\"")
    return evaluation


def override_teacher_score(session: Session, new_score: float, rationale: str):
    """
    Teacher overrides the score. 
    Enforces atomic governance: updates evaluation AND records immutable audit log.
    """
    print("\n[4/5] Human-in-the-Loop Moderation: Executing Teacher Score Override...")
    
    teacher = session.scalars(select(UserModel).where(UserModel.role == "teacher")).first()
    evaluation = session.scalars(select(EvaluationModel)).first()

    old_score = evaluation.final_score

    # 1. Update Evaluation
    evaluation.teacher_score = new_score
    evaluation.final_score = new_score
    evaluation.is_verified = True
    evaluation.verified_by = teacher.id
    evaluation.updated_at = datetime.now(timezone.utc)

    # 2. Add Immutable Audit Log with Mandatory Academic Rationale
    audit_entry = AuditLogModel(
        id=str(uuid.uuid4()),
        entity_name="evaluations",
        entity_id=evaluation.id,
        action="SCORE_OVERRIDE",
        performed_by=teacher.id,
        old_value=f"{old_score} marks",
        new_value=f"{new_score} marks",
        academic_rationale=rationale,
        timestamp=datetime.now(timezone.utc)
    )
    session.add(audit_entry)
    session.commit()

    print(f"      -> Score updated from {old_score} to {new_score} marks.")
    print(f"      -> Verification status: CERTIFIED & LOCKED.")
    print(f"      -> Immutable Audit Log Recorded:")
    print(f"         - Evaluator: {teacher.full_name}")
    print(f"         - Mandatory Rationale: \"{rationale}\"")


def generate_analytics_report(session: Session):
    """Generates analytical report from the database."""
    print("\n[5/5] Generating Academic Verification & Audit Trail Summary...")
    
    stmt = (
        select(
            UserModel.full_name.label("student_name"),
            QuestionModel.question_number,
            QuestionModel.max_marks,
            EvaluationModel.ai_score,
            EvaluationModel.final_score,
            EvaluationModel.is_verified,
            AuditLogModel.academic_rationale,
            AuditLogModel.performed_by,
            AuditLogModel.timestamp
        )
        .join(QuestionModel, EvaluationModel.question_id == QuestionModel.id)
        .join(UserModel, EvaluationModel.student_id == UserModel.id)
        .outerjoin(AuditLogModel, AuditLogModel.entity_id == EvaluationModel.id)
    )

    results = session.execute(stmt).all()
    teacher = session.scalars(select(UserModel).where(UserModel.role == "teacher")).first()

    print("\n" + "=" * 88)
    print("                INTELLIGRADE™ AUDIT PROVENANCE & CERTIFICATION LEDGER")
    print("=" * 88)
    for row in results:
        print(f" Student Name        : {row.student_name}")
        print(f" Question Evaluated  : Question #{row.question_number} (Max Marks: {row.max_marks})")
        print(f" AI Proposed Score   : {row.ai_score} / {row.max_marks}")
        print(f" Certified Mark      : {row.final_score} / {row.max_marks}")
        print(f" Verification Status : {'[CERTIFIED & VERIFIED]' if row.is_verified else '[PENDING MODERATION]'}")
        if row.academic_rationale:
            print(f" Moderation Action   : SCORE_OVERRIDE (+1.0 Mark)")
            print(f" Verified By         : {teacher.full_name}")
            print(f" Academic Rationale  : \"{row.academic_rationale}\"")
            print(f" Provenance Timestamp: {row.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 88 + "\n")


# ── 4. MAIN EXECUTION WORKFLOW ────────────────────────────────────────────────
def main():
    init_database()
    with SessionLocal() as session:
        try:
            seed_master_data(session)
            record_ai_evaluation(session)
            
            # Simulate a teacher overriding the AI mark with a documented rationale
            override_teacher_score(
                session=session,
                new_score=9.5,
                rationale="Awarded +1.0 mark: Student provided a valid Write-Ahead Logging (WAL) recovery diagram on page 2 that was verified manually."
            )
            
            generate_analytics_report(session)
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Transaction failed: {e}")
            raise
        finally:
            session.close()


if __name__ == "__main__":
    main()

