"""
application/use_cases/reports/generate_plagiarism_report_pdf_use_case.py
"""

from __future__ import annotations
import uuid
from datetime import datetime

from app.domain.repositories.plagiarism_repository import PlagiarismRepository
from app.domain.repositories.plagiarism_similarity_repository import PlagiarismSimilarityRepository
from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.student_repository import StudentRepository
from app.domain.repositories.question_mapping_repository import QuestionMappingRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.reports.weasyprint_pdf_service import WeasyPrintPDFService

from app.domain.exceptions.domain_exception import EntityNotFoundException


class GeneratePlagiarismReportPDFUseCase:
    """
    Use Case: Gathers plagiarism check metrics, comparative students profile,
    and question-level similarity details (side-by-side text comparisons) to
    produce a detailed plagiarism analysis PDF.
    """

    def __init__(
        self,
        plagiarism_repo: PlagiarismRepository,
        plagiarism_similarity_repo: PlagiarismSimilarityRepository,
        answer_sheet_repo: AnswerSheetRepository,
        student_repo: StudentRepository,
        question_mapping_repo: QuestionMappingRepository,
        user_repo: UserRepository,
        pdf_service: WeasyPrintPDFService
    ) -> None:
        self.plagiarism_repo = plagiarism_repo
        self.plagiarism_similarity_repo = plagiarism_similarity_repo
        self.answer_sheet_repo = answer_sheet_repo
        self.student_repo = student_repo
        self.question_mapping_repo = question_mapping_repo
        self.user_repo = user_repo
        self.pdf_service = pdf_service

    async def execute(self, report_id: uuid.UUID) -> bytes:
        # 1. Fetch Plagiarism Report
        report = await self.plagiarism_repo.get_by_id(report_id)
        if not report:
            raise EntityNotFoundException("PlagiarismReport", report_id)

        # 2. Fetch Source & Target Answer Sheets & Students
        src_sheet = await self.answer_sheet_repo.get_by_id(report.source_answer_sheet_id)
        target_sheet = await self.answer_sheet_repo.get_by_id(report.target_answer_sheet_id)
        
        student_a_name = "N/A"
        student_a_number = "N/A"
        if src_sheet:
            student_a = await self.student_repo.get_by_id(src_sheet.student_id)
            if student_a:
                student_a_name = student_a.full_name
                student_a_number = student_a.student_number

        student_b_name = "N/A"
        student_b_number = "N/A"
        if target_sheet:
            student_b = await self.student_repo.get_by_id(target_sheet.student_id)
            if student_b:
                student_b_name = student_b.full_name
                student_b_number = student_b.student_number

        # 3. Fetch Plagiarism Similarity records for this pair
        sims = await self.plagiarism_similarity_repo.list_by_pair(
            report.source_answer_sheet_id, 
            report.target_answer_sheet_id
        )

        # 4. Resolve Segment Mappings & Texts
        similarity_segments = []
        overall_semantic = 0.0
        overall_lexical = 0.0
        overall_overlap = 0.0

        if len(sims) > 0:
            semantic_sum = 0.0
            lexical_sum = 0.0
            overlap_sum = 0.0

            for sim in sims:
                # Fetch Question Mapping texts
                src_mapping = await self.question_mapping_repo.get_by_id(sim.source_question_mapping_id)
                target_mapping = await self.question_mapping_repo.get_by_id(sim.target_question_mapping_id)

                src_text = src_mapping.extracted_answer_text if src_mapping else ""
                target_text = target_mapping.extracted_answer_text if target_mapping else ""
                
                q_label = None
                if src_mapping:
                    q_label = src_mapping.detected_question_label
                if not q_label and target_mapping:
                    q_label = target_mapping.detected_question_label
                q_title = f"Question {q_label}" if q_label else "Compared Answer Block"

                similarity_segments.append({
                    "question_title": q_title,
                    "semantic_similarity": sim.semantic_similarity,
                    "lexical_similarity": sim.lexical_similarity,
                    "overlap_similarity": sim.overlap_similarity,
                    "final_similarity": sim.final_similarity,
                    "risk_level": sim.risk_level,
                    "source_text": src_text,
                    "target_text": target_text
                })

                semantic_sum += sim.semantic_similarity
                lexical_sum += sim.lexical_similarity
                overlap_sum += sim.overlap_similarity

            overall_semantic = semantic_sum / len(sims)
            overall_lexical = lexical_sum / len(sims)
            overall_overlap = overlap_sum / len(sims)

        # 5. Resolve Reviewer Details
        reviewer_name = None
        if report.reviewed_by:
            reviewer = await self.user_repo.get_by_id(report.reviewed_by)
            if reviewer:
                reviewer_name = reviewer.full_name

        # 6. Format status label
        review_status = report.status.value if hasattr(report.status, "value") else str(report.status)

        context = {
            "report_id": str(report_id),
            "created_at": report.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "student_a_name": student_a_name,
            "student_a_number": student_a_number,
            "student_b_name": student_b_name,
            "student_b_number": student_b_number,
            "review_status": review_status.upper(),
            "risk_level": report.risk_level,
            "similarity_percentage": report.similarity_percentage,
            "semantic_similarity": overall_semantic,
            "lexical_similarity": overall_lexical,
            "overlap_similarity": overall_overlap,
            "similarity_segments": similarity_segments,
            "teacher_notes": report.teacher_notes,
            "reviewed_by": reviewer_name,
            "reviewed_at": report.reviewed_at.strftime("%Y-%m-%d %H:%M:%S") if report.reviewed_at else None
        }

        # 7. Render Report
        return self.pdf_service.generate_pdf("plagiarism_report.html", context)
