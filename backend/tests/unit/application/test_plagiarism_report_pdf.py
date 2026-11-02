"""
tests/unit/application/test_plagiarism_report_pdf.py — Unit Tests for Plagiarism Report PDF Use Case
"""

from __future__ import annotations
import sys
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Mock WeasyPrint HTML class to prevent GTK library load error
if 'weasyprint' in sys.modules:
    mock_weasyprint = sys.modules['weasyprint']
    mock_html_class = mock_weasyprint.HTML
else:
    mock_weasyprint = MagicMock()
    mock_html_class = MagicMock()
    mock_weasyprint.HTML = mock_html_class
    sys.modules['weasyprint'] = mock_weasyprint

import pytest
from app.application.use_cases.reports.generate_plagiarism_report_pdf_use_case import GeneratePlagiarismReportPDFUseCase
from app.infrastructure.reports.weasyprint_pdf_service import WeasyPrintPDFService

# Repositories interfaces/concrete mocks
from app.domain.repositories.plagiarism_repository import PlagiarismRepository
from app.domain.repositories.plagiarism_similarity_repository import PlagiarismSimilarityRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.student_repository import StudentRepository
from app.domain.repositories.question_mapping_repository import QuestionMappingRepository
from app.domain.repositories.user_repository import UserRepository


@pytest.fixture
def mock_pdf_service():
    service = WeasyPrintPDFService()
    mock_html_class.return_value.write_pdf.return_value = b"%PDF-1.4 mock plagiarism report bytes"
    return service


@pytest.mark.asyncio
async def test_generate_plagiarism_report_pdf_success(mock_pdf_service):
    report_id = uuid.uuid4()
    src_sheet_id = uuid.uuid4()
    target_sheet_id = uuid.uuid4()
    student_a_id = uuid.uuid4()
    student_b_id = uuid.uuid4()
    reviewer_user_id = uuid.uuid4()
    similarity_id = uuid.uuid4()
    src_mapping_id = uuid.uuid4()
    target_mapping_id = uuid.uuid4()

    # Mocks
    mock_report = MagicMock()
    mock_report.id = report_id
    mock_report.source_answer_sheet_id = src_sheet_id
    mock_report.target_answer_sheet_id = target_sheet_id
    mock_report.similarity_percentage = 45.5
    mock_report.risk_level = "SUSPICIOUS"
    mock_report.status = MagicMock()
    mock_report.status.value = "reviewed"
    mock_report.teacher_notes = "Similar structure and lexical overlap detected in Question 2."
    mock_report.reviewed_by = reviewer_user_id
    mock_report.reviewed_at = datetime(2026, 6, 21, 15, 0, 0)
    mock_report.created_at = datetime(2026, 6, 21, 10, 0, 0)

    mock_src_sheet = MagicMock()
    mock_src_sheet.id = src_sheet_id
    mock_src_sheet.student_id = student_a_id

    mock_target_sheet = MagicMock()
    mock_target_sheet.id = target_sheet_id
    mock_target_sheet.student_id = student_b_id

    mock_student_a = MagicMock()
    mock_student_a.id = student_a_id
    mock_student_a.full_name = "Alice Vance"
    mock_student_a.student_number = "STU-001"

    mock_student_b = MagicMock()
    mock_student_b.id = student_b_id
    mock_student_b.full_name = "Bob Miller"
    mock_student_b.student_number = "STU-002"

    mock_sim = MagicMock()
    mock_sim.id = similarity_id
    mock_sim.source_question_mapping_id = src_mapping_id
    mock_sim.target_question_mapping_id = target_mapping_id
    mock_sim.semantic_similarity = 0.8
    mock_sim.lexical_similarity = 0.7
    mock_sim.overlap_similarity = 0.6
    mock_sim.final_similarity = 0.7
    mock_sim.risk_level = "SUSPICIOUS"

    mock_src_mapping = MagicMock()
    mock_src_mapping.id = src_mapping_id
    mock_src_mapping.extracted_answer_text = "The quick brown fox jumps over the lazy dog."
    mock_src_mapping.detected_question_label = "2"

    mock_target_mapping = MagicMock()
    mock_target_mapping.id = target_mapping_id
    mock_target_mapping.extracted_answer_text = "A quick brown fox jumped over a lazy dog."
    mock_target_mapping.detected_question_label = "2"

    mock_reviewer = MagicMock()
    mock_reviewer.id = reviewer_user_id
    mock_reviewer.full_name = "Dr. Robert Smith"

    # Repository Mocks setup
    plagiarism_repo = MagicMock(spec=PlagiarismRepository)
    plagiarism_repo.get_by_id = AsyncMock(return_value=mock_report)

    plagiarism_similarity_repo = MagicMock(spec=PlagiarismSimilarityRepository)
    plagiarism_similarity_repo.list_by_pair = AsyncMock(return_value=[mock_sim])

    answer_sheet_repo = MagicMock(spec=AnswerSheetRepository)
    # Return source sheet for first call, target sheet for second call
    answer_sheet_repo.get_by_id = AsyncMock(side_effect=lambda sheet_id: mock_src_sheet if sheet_id == src_sheet_id else mock_target_sheet)

    student_repo = MagicMock(spec=StudentRepository)
    student_repo.get_by_id = AsyncMock(side_effect=lambda stu_id: mock_student_a if stu_id == student_a_id else mock_student_b)

    question_mapping_repo = MagicMock(spec=QuestionMappingRepository)
    question_mapping_repo.get_by_id = AsyncMock(side_effect=lambda mapping_id: mock_src_mapping if mapping_id == src_mapping_id else mock_target_mapping)

    user_repo = MagicMock(spec=UserRepository)
    user_repo.get_by_id = AsyncMock(return_value=mock_reviewer)

    use_case = GeneratePlagiarismReportPDFUseCase(
        plagiarism_repo=plagiarism_repo,
        plagiarism_similarity_repo=plagiarism_similarity_repo,
        answer_sheet_repo=answer_sheet_repo,
        student_repo=student_repo,
        question_mapping_repo=question_mapping_repo,
        user_repo=user_repo,
        pdf_service=mock_pdf_service
    )

    with patch.object(mock_pdf_service, 'generate_pdf', return_value=b"%PDF-1.4 mock plagiarism report bytes") as mock_generate:
        pdf_bytes = await use_case.execute(report_id=report_id)
        
        assert pdf_bytes == b"%PDF-1.4 mock plagiarism report bytes"
        mock_generate.assert_called_once()
        
        template_name, context = mock_generate.call_args[0]
        assert template_name == "plagiarism_report.html"
        
        # Verify context details mapping
        assert context["report_id"] == str(report_id)
        assert context["created_at"] == "2026-06-21 10:00:00"
        assert context["student_a_name"] == "Alice Vance"
        assert context["student_a_number"] == "STU-001"
        assert context["student_b_name"] == "Bob Miller"
        assert context["student_b_number"] == "STU-002"
        assert context["review_status"] == "REVIEWED"
        assert context["risk_level"] == "SUSPICIOUS"
        assert context["similarity_percentage"] == 45.5
        
        # Verify overall similarity calculations
        assert context["semantic_similarity"] == 0.8
        assert context["lexical_similarity"] == 0.7
        assert context["overlap_similarity"] == 0.6
        
        # Verify segments details
        assert len(context["similarity_segments"]) == 1
        seg_mapped = context["similarity_segments"][0]
        assert seg_mapped["question_title"] == "Question 2"
        assert seg_mapped["semantic_similarity"] == 0.8
        assert seg_mapped["lexical_similarity"] == 0.7
        assert seg_mapped["overlap_similarity"] == 0.6
        assert seg_mapped["final_similarity"] == 0.7
        assert seg_mapped["risk_level"] == "SUSPICIOUS"
        assert seg_mapped["source_text"] == "The quick brown fox jumps over the lazy dog."
        assert seg_mapped["target_text"] == "A quick brown fox jumped over a lazy dog."
        
        # Verify reviewer details
        assert context["reviewed_by"] == "Dr. Robert Smith"
        assert context["reviewed_at"] == "2026-06-21 15:00:00"
        assert context["teacher_notes"] == "Similar structure and lexical overlap detected in Question 2."
