"""
tests/unit/application/test_plagiarism_use_cases.py — Unit Tests for Plagiarism Use Cases
"""

from __future__ import annotations

import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.domain.entities.answer_sheet import AnswerSheet
from app.domain.entities.question_mapping import QuestionMapping
from app.domain.entities.plagiarism_report import PlagiarismReport
from app.domain.entities.plagiarism_similarity import PlagiarismSimilarity
from app.core.constants import AnswerSheetStatus, PlagiarismStatus, AuditAction

from app.application.use_cases.plagiarism.detect_answer_sheet_plagiarism_use_case import DetectAnswerSheetPlagiarismUseCase
from app.application.use_cases.plagiarism.review_plagiarism_use_case import ReviewPlagiarismUseCase


@pytest.fixture
def mock_plagiarism_repos():
    return {
        "answer_sheet_repo": AsyncMock(),
        "question_mapping_repo": AsyncMock(),
        "plagiarism_repo": AsyncMock(),
        "plagiarism_similarity_repo": AsyncMock(),
        "notification_repo": AsyncMock(),
        "audit_repo": AsyncMock(),
        "exam_repo": AsyncMock()
    }


@pytest.fixture
def mock_score_service():
    service = MagicMock()
    # Stub compute_scores to return high plagiarism (0.85) by default
    service.compute_scores.return_value = {
        "semantic": 0.9,
        "lexical": 0.8,
        "overlap": 0.8,
        "final": 0.85
    }
    service.get_embedding.return_value = [0.1] * 768
    return service


@pytest.mark.asyncio
async def test_detect_answer_sheet_plagiarism_basic_flow(mock_plagiarism_repos, mock_score_service):
    use_case = DetectAnswerSheetPlagiarismUseCase(
        answer_sheet_repo=mock_plagiarism_repos["answer_sheet_repo"],
        question_mapping_repo=mock_plagiarism_repos["question_mapping_repo"],
        plagiarism_repo=mock_plagiarism_repos["plagiarism_repo"],
        plagiarism_similarity_repo=mock_plagiarism_repos["plagiarism_similarity_repo"],
        notification_repo=mock_plagiarism_repos["notification_repo"],
        audit_repo=mock_plagiarism_repos["audit_repo"],
        exam_repo=mock_plagiarism_repos["exam_repo"],
        plagiarism_score_service=mock_score_service
    )

    sheet_id1 = uuid.uuid4()
    sheet_id2 = uuid.uuid4()
    exam_id = uuid.uuid4()
    question_id = uuid.uuid4()

    source_sheet = AnswerSheet(
        id=sheet_id1,
        exam_id=exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="s1.pdf",
        stored_filename="s1.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash1",
        status=AnswerSheetStatus.EVALUATION_COMPLETED
    )
    target_sheet = AnswerSheet(
        id=sheet_id2,
        exam_id=exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="s2.pdf",
        stored_filename="s2.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash2",
        status=AnswerSheetStatus.EVALUATION_COMPLETED
    )

    mock_plagiarism_repos["answer_sheet_repo"].get_by_id.return_value = source_sheet
    mock_plagiarism_repos["answer_sheet_repo"].get_all_by_exam_id.return_value = [source_sheet, target_sheet]

    source_mapping = QuestionMapping(
        id=uuid.uuid4(),
        answer_sheet_id=sheet_id1,
        question_id=question_id,
        detected_question_number=1,
        detected_question_label="Q1",
        extracted_answer_text="This is a long student answer that is longer than 20 characters.",
        start_page=1,
        end_page=1,
        mapping_confidence=0.8,
        status="MAPPED"
    )
    target_mapping = QuestionMapping(
        id=uuid.uuid4(),
        answer_sheet_id=sheet_id2,
        question_id=question_id,
        detected_question_number=1,
        detected_question_label="Q1",
        extracted_answer_text="This is another student answer that is also longer than 20 characters.",
        start_page=1,
        end_page=1,
        mapping_confidence=0.8,
        status="MAPPED"
    )

    mock_plagiarism_repos["question_mapping_repo"].list_by_answer_sheet_id.side_effect = lambda sid: (
        [source_mapping] if sid == sheet_id1 else [target_mapping]
    )

    mock_plagiarism_repos["exam_repo"].get_by_id.return_value = MagicMock(created_by=uuid.uuid4())

    res = await use_case.execute(sheet_id1)

    assert res["status"] == "COMPLETED"
    assert res["created_reports"] == 1
    assert res["highest_similarity"] == 0.85

    # Verify status changed to PLAGIARISM_REVIEW_PENDING
    assert source_sheet.status == AnswerSheetStatus.PLAGIARISM_REVIEW_PENDING
    assert target_sheet.status == AnswerSheetStatus.PLAGIARISM_REVIEW_PENDING
    assert source_sheet.plagiarism_flagged is True

    # Audit log called for PLAGIARISM_DETECTED
    mock_plagiarism_repos["audit_repo"].save.assert_called()


@pytest.mark.asyncio
async def test_detect_answer_sheet_plagiarism_skips_same_student(mock_plagiarism_repos, mock_score_service):
    use_case = DetectAnswerSheetPlagiarismUseCase(
        answer_sheet_repo=mock_plagiarism_repos["answer_sheet_repo"],
        question_mapping_repo=mock_plagiarism_repos["question_mapping_repo"],
        plagiarism_repo=mock_plagiarism_repos["plagiarism_repo"],
        plagiarism_similarity_repo=mock_plagiarism_repos["plagiarism_similarity_repo"],
        notification_repo=mock_plagiarism_repos["notification_repo"],
        audit_repo=mock_plagiarism_repos["audit_repo"],
        exam_repo=mock_plagiarism_repos["exam_repo"],
        plagiarism_score_service=mock_score_service
    )

    sheet_id1 = uuid.uuid4()
    sheet_id2 = uuid.uuid4()
    student_id = uuid.uuid4() # Same student
    exam_id = uuid.uuid4()

    source_sheet = AnswerSheet(
        id=sheet_id1,
        exam_id=exam_id,
        student_id=student_id,
        uploaded_by=uuid.uuid4(),
        original_filename="s1.pdf",
        stored_filename="s1.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash1",
        status=AnswerSheetStatus.EVALUATION_COMPLETED
    )
    target_sheet = AnswerSheet(
        id=sheet_id2,
        exam_id=exam_id,
        student_id=student_id, # Same student submission
        uploaded_by=uuid.uuid4(),
        original_filename="s2.pdf",
        stored_filename="s2.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash2",
        status=AnswerSheetStatus.EVALUATION_COMPLETED
    )

    mock_plagiarism_repos["answer_sheet_repo"].get_by_id.return_value = source_sheet
    mock_plagiarism_repos["answer_sheet_repo"].get_all_by_exam_id.return_value = [source_sheet, target_sheet]

    mock_plagiarism_repos["question_mapping_repo"].list_by_answer_sheet_id.return_value = [MagicMock()]

    res = await use_case.execute(sheet_id1)
    # Target sheets should be 0 because we prevent self-comparison
    assert res["compared_sheets"] == 0


@pytest.mark.asyncio
async def test_detect_answer_sheet_plagiarism_state_protection(mock_plagiarism_repos, mock_score_service):
    use_case = DetectAnswerSheetPlagiarismUseCase(
        answer_sheet_repo=mock_plagiarism_repos["answer_sheet_repo"],
        question_mapping_repo=mock_plagiarism_repos["question_mapping_repo"],
        plagiarism_repo=mock_plagiarism_repos["plagiarism_repo"],
        plagiarism_similarity_repo=mock_plagiarism_repos["plagiarism_similarity_repo"],
        notification_repo=mock_plagiarism_repos["notification_repo"],
        audit_repo=mock_plagiarism_repos["audit_repo"],
        exam_repo=mock_plagiarism_repos["exam_repo"],
        plagiarism_score_service=mock_score_service
    )

    sheet_id1 = uuid.uuid4()
    sheet_id2 = uuid.uuid4()
    exam_id = uuid.uuid4()
    question_id = uuid.uuid4()

    # Source is already VERIFIED (protected state)
    source_sheet = AnswerSheet(
        id=sheet_id1,
        exam_id=exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="s1.pdf",
        stored_filename="s1.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash1",
        status=AnswerSheetStatus.VERIFIED
    )
    target_sheet = AnswerSheet(
        id=sheet_id2,
        exam_id=exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="s2.pdf",
        stored_filename="s2.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash2",
        status=AnswerSheetStatus.EVALUATION_COMPLETED
    )

    mock_plagiarism_repos["answer_sheet_repo"].get_by_id.return_value = source_sheet
    mock_plagiarism_repos["answer_sheet_repo"].get_all_by_exam_id.return_value = [source_sheet, target_sheet]

    source_mapping = QuestionMapping(
        id=uuid.uuid4(),
        answer_sheet_id=sheet_id1,
        question_id=question_id,
        detected_question_number=1,
        detected_question_label="Q1",
        extracted_answer_text="This is a long student answer that is longer than 20 characters.",
        start_page=1,
        end_page=1,
        mapping_confidence=0.8,
        status="MAPPED"
    )
    target_mapping = QuestionMapping(
        id=uuid.uuid4(),
        answer_sheet_id=sheet_id2,
        question_id=question_id,
        detected_question_number=1,
        detected_question_label="Q1",
        extracted_answer_text="This is another student answer that is also longer than 20 characters.",
        start_page=1,
        end_page=1,
        mapping_confidence=0.8,
        status="MAPPED"
    )

    mock_plagiarism_repos["question_mapping_repo"].list_by_answer_sheet_id.side_effect = lambda sid: (
        [source_mapping] if sid == sheet_id1 else [target_mapping]
    )

    res = await use_case.execute(sheet_id1)

    # Source status must remain VERIFIED (protection check)
    assert source_sheet.status == AnswerSheetStatus.VERIFIED
    assert source_sheet.plagiarism_flagged is True
    # Target status can still transition to PLAGIARISM_REVIEW_PENDING since it was not in a protected state
    assert target_sheet.status == AnswerSheetStatus.PLAGIARISM_REVIEW_PENDING


@pytest.mark.asyncio
async def test_review_plagiarism_use_case_confirmed(mock_plagiarism_repos):
    use_case = ReviewUseCase = ReviewPlagiarismUseCase(
        plagiarism_repo=mock_plagiarism_repos["plagiarism_repo"],
        answer_sheet_repo=mock_plagiarism_repos["answer_sheet_repo"],
        audit_repo=mock_plagiarism_repos["audit_repo"]
    )

    report_id = uuid.uuid4()
    sheet_id1 = uuid.uuid4()
    sheet_id2 = uuid.uuid4()

    report = PlagiarismReport(
        id=report_id,
        exam_id=uuid.uuid4(),
        source_answer_sheet_id=sheet_id1,
        target_answer_sheet_id=sheet_id2,
        similarity_percentage=85.0,
        highest_similarity=0.85,
        risk_level="HIGH_RISK",
        status=PlagiarismStatus.DETECTED
    )

    mock_plagiarism_repos["plagiarism_repo"].get_by_id.return_value = report

    res = await use_case.execute(
        report_id=report_id,
        status="CONFIRMED_PLAGIARISM",
        teacher_notes="Confirmed copied.",
        user_id=uuid.uuid4()
    )

    assert res["status"] == "CONFIRMED_PLAGIARISM"
    assert report.status == PlagiarismStatus.CONFIRMED_PLAGIARISM
    # Audit log check: PLAGIARISM_CONFIRMED should be fired
    mock_plagiarism_repos["audit_repo"].save.assert_called_once()


@pytest.mark.asyncio
async def test_detect_plagiarism_exam_wide_flow(mock_plagiarism_repos):
    from app.application.use_cases.plagiarism.detect_plagiarism_use_case import DetectPlagiarismUseCase
    
    mock_detect_sheet = AsyncMock()
    mock_detect_sheet.execute.return_value = {
        "status": "COMPLETED",
        "created_reports": 1,
        "highest_similarity": 0.85
    }
    
    use_case = DetectPlagiarismUseCase(
        answer_sheet_repo=mock_plagiarism_repos["answer_sheet_repo"],
        plagiarism_repo=mock_plagiarism_repos["plagiarism_repo"],
        plagiarism_similarity_repo=mock_plagiarism_repos["plagiarism_similarity_repo"],
        detect_sheet_use_case=mock_detect_sheet
    )
    
    exam_id = uuid.uuid4()
    sheet_id1 = uuid.uuid4()
    sheet_id2 = uuid.uuid4()
    
    mock_sheets = [
        MagicMock(id=sheet_id1),
        MagicMock(id=sheet_id2)
    ]
    mock_plagiarism_repos["answer_sheet_repo"].get_all_by_exam_id.return_value = mock_sheets
    
    res = await use_case.execute(exam_id)
    
    assert res["status"] == "COMPLETED"
    assert res["total_sheets"] == 2
    assert res["scanned_sheets"] == 2
    
    mock_plagiarism_repos["plagiarism_similarity_repo"].delete_by_answer_sheet_id.assert_any_call(sheet_id1)
    mock_plagiarism_repos["plagiarism_similarity_repo"].delete_by_answer_sheet_id.assert_any_call(sheet_id2)
    mock_plagiarism_repos["plagiarism_repo"].delete_by_exam_id.assert_called_once_with(exam_id)
    assert mock_detect_sheet.execute.call_count == 2


@pytest.mark.asyncio
async def test_detect_answer_sheet_plagiarism_deduplication(mock_plagiarism_repos, mock_score_service):
    use_case = DetectAnswerSheetPlagiarismUseCase(
        answer_sheet_repo=mock_plagiarism_repos["answer_sheet_repo"],
        question_mapping_repo=mock_plagiarism_repos["question_mapping_repo"],
        plagiarism_repo=mock_plagiarism_repos["plagiarism_repo"],
        plagiarism_similarity_repo=mock_plagiarism_repos["plagiarism_similarity_repo"],
        notification_repo=mock_plagiarism_repos["notification_repo"],
        audit_repo=mock_plagiarism_repos["audit_repo"],
        exam_repo=mock_plagiarism_repos["exam_repo"],
        plagiarism_score_service=mock_score_service
    )

    sheet_id1 = uuid.uuid4()
    sheet_id2 = uuid.uuid4()
    # Normalize order
    if sheet_id1 < sheet_id2:
        smaller_id, larger_id = sheet_id1, sheet_id2
    else:
        smaller_id, larger_id = sheet_id2, sheet_id1

    processed_pairs = {(smaller_id, larger_id)}

    source_sheet = AnswerSheet(
        id=sheet_id1,
        exam_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="s1.pdf",
        stored_filename="s1.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash1",
        status=AnswerSheetStatus.EVALUATION_COMPLETED
    )
    target_sheet = AnswerSheet(
        id=sheet_id2,
        exam_id=source_sheet.exam_id,
        student_id=uuid.uuid4(),
        uploaded_by=uuid.uuid4(),
        original_filename="s2.pdf",
        stored_filename="s2.pdf",
        file_path="uploads/",
        file_size_bytes=1000,
        mime_type="application/pdf",
        file_hash="hash2",
        status=AnswerSheetStatus.EVALUATION_COMPLETED
    )

    mock_plagiarism_repos["answer_sheet_repo"].get_by_id.return_value = source_sheet
    mock_plagiarism_repos["answer_sheet_repo"].get_all_by_exam_id.return_value = [source_sheet, target_sheet]

    res = await use_case.execute(sheet_id1, processed_pairs=processed_pairs)
    
    # It should skip comparing target_sheet because it is already in processed_pairs!
    assert res["compared_sheets"] == 0


@pytest.mark.asyncio
async def test_get_exam_plagiarism_summary(mock_plagiarism_repos):
    from app.application.use_cases.plagiarism.get_plagiarism_report_use_case import GetPlagiarismReportUseCase
    
    use_case = GetPlagiarismReportUseCase(
        plagiarism_repo=mock_plagiarism_repos["plagiarism_repo"],
        plagiarism_similarity_repo=mock_plagiarism_repos["plagiarism_similarity_repo"],
        answer_sheet_repo=mock_plagiarism_repos["answer_sheet_repo"]
    )
    
    exam_id = uuid.uuid4()
    sheet_id1 = uuid.uuid4()
    sheet_id2 = uuid.uuid4()
    
    mock_reports = [
        PlagiarismReport(
            id=uuid.uuid4(),
            exam_id=exam_id,
            source_answer_sheet_id=sheet_id1,
            target_answer_sheet_id=sheet_id2,
            similarity_percentage=85.0,
            highest_similarity=0.85,
            risk_level="HIGH_RISK",
            status=PlagiarismStatus.DETECTED
        )
    ]
    mock_plagiarism_repos["plagiarism_repo"].get_by_exam_id.return_value = mock_reports
    
    mock_sheets = [
        MagicMock(id=sheet_id1, plagiarism_flagged=True),
        MagicMock(id=sheet_id2, plagiarism_flagged=False)
    ]
    mock_plagiarism_repos["answer_sheet_repo"].get_all_by_exam_id.return_value = mock_sheets
    
    summary = await use_case.get_exam_summary(exam_id)
    
    assert summary["exam_id"] == str(exam_id)
    assert summary["total_reports"] == 1
    assert summary["high_risk_count"] == 1
    assert summary["highest_similarity"] == 0.85
    assert summary["flagged_sheets_count"] == 1
    assert len(summary["top_flagged_pairs"]) == 1
