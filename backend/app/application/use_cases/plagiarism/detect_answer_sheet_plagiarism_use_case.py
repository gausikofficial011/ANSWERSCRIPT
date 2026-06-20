"""
application/use_cases/plagiarism/detect_answer_sheet_plagiarism_use_case.py — Detect Answer Sheet Plagiarism Use Case
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List

from app.domain.entities.plagiarism_report import PlagiarismReport
from app.domain.entities.plagiarism_similarity import PlagiarismSimilarity
from app.domain.entities.notification import Notification
from app.domain.entities.audit_log import AuditLog

from app.domain.repositories.answer_sheet_repository import AnswerSheetRepository
from app.domain.repositories.question_mapping_repository import QuestionMappingRepository
from app.domain.repositories.plagiarism_repository import PlagiarismRepository
from app.domain.repositories.plagiarism_similarity_repository import PlagiarismSimilarityRepository
from app.domain.repositories.notification_repository import NotificationRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.repositories.exam_repository import ExamRepository

from app.infrastructure.ai.plagiarism_score_service import PlagiarismScoreService
from app.core.constants import (
    AnswerSheetStatus,
    PlagiarismStatus,
    NotificationType,
    NotificationCategory,
    AuditAction,
    AuditStatus
)
from app.domain.exceptions.domain_exception import EntityNotFoundException

logger = logging.getLogger(__name__)


class DetectAnswerSheetPlagiarismUseCase:
    """
    Scans a student answer sheet for plagiarism against all other sheets in the same exam.
    Enforces Same Exam, Question-to-Question, self-comparison prevention, and scalability rules.
    """

    def __init__(
        self,
        answer_sheet_repo: AnswerSheetRepository,
        question_mapping_repo: QuestionMappingRepository,
        plagiarism_repo: PlagiarismRepository,
        plagiarism_similarity_repo: PlagiarismSimilarityRepository,
        notification_repo: NotificationRepository,
        audit_repo: AuditLogRepository,
        exam_repo: ExamRepository,
        plagiarism_score_service: PlagiarismScoreService
    ) -> None:
        self.answer_sheet_repo = answer_sheet_repo
        self.question_mapping_repo = question_mapping_repo
        self.plagiarism_repo = plagiarism_repo
        self.plagiarism_similarity_repo = plagiarism_similarity_repo
        self.notification_repo = notification_repo
        self.audit_repo = audit_repo
        self.exam_repo = exam_repo
        self.plagiarism_score_service = plagiarism_score_service

    async def execute(
        self,
        answer_sheet_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
        processed_pairs: set[tuple[uuid.UUID, uuid.UUID]] | None = None
    ) -> dict:
        """
        Executes plagiarism detection for a source answer sheet.
        """
        now = datetime.now(timezone.utc)
        user_id = user_id or uuid.UUID("00000000-0000-0000-0000-000000000000")

        # 1. Fetch source answer sheet
        source_sheet = await self.answer_sheet_repo.get_by_id(answer_sheet_id)
        if not source_sheet:
            raise EntityNotFoundException(entity_type="AnswerSheet", entity_id=answer_sheet_id)

        # 2. Fetch all other sheets for the same exam (Same Exam Restriction)
        all_sheets = await self.answer_sheet_repo.get_all_by_exam_id(source_sheet.exam_id)
        
        # Prevent self-comparison and compare only other students' sheets
        target_sheets = [
            s for s in all_sheets 
            if s.id != source_sheet.id and s.student_id != source_sheet.student_id
        ]

        if not target_sheets:
            return {
                "answer_sheet_id": str(answer_sheet_id),
                "compared_sheets": 0,
                "created_reports": 0,
                "status": "NO_TARGET_SHEETS"
            }

        # 3. Fetch question mappings for the source sheet
        source_mappings = await self.question_mapping_repo.list_by_answer_sheet_id(source_sheet.id)
        if not source_mappings:
            return {
                "answer_sheet_id": str(answer_sheet_id),
                "compared_sheets": 0,
                "created_reports": 0,
                "status": "NO_SOURCE_MAPPINGS"
            }

        # Embeddings cache for the plagiarism run (Scalability Protection)
        embeddings_cache: dict[uuid.UUID, list[float]] = {}

        created_reports_count = 0
        exam_highest_similarity = 0.0
        compared_sheets_count = 0

        # State protection checks: should we preserve status?
        protected_statuses = {"TEACHER_REVIEW_PENDING", "VERIFIED", "PUBLISHED"}

        # 4. Compare source sheet against each target sheet
        for target_sheet in target_sheets:
            # Check processed pairs to avoid duplicate comparisons
            if source_sheet.id < target_sheet.id:
                s_id, t_id = source_sheet.id, target_sheet.id
            else:
                s_id, t_id = target_sheet.id, source_sheet.id

            if processed_pairs is not None and (s_id, t_id) in processed_pairs:
                continue

            target_mappings = await self.question_mapping_repo.list_by_answer_sheet_id(target_sheet.id)
            if not target_mappings:
                if processed_pairs is not None:
                    processed_pairs.add((s_id, t_id))
                continue

            compared_sheets_count += 1

            # Normalize pairs so that s_sheet always has the smaller ID
            if source_sheet.id < target_sheet.id:
                s_sheet = source_sheet
                t_sheet = target_sheet
                s_mappings = source_mappings
                t_mappings = target_mappings
            else:
                s_sheet = target_sheet
                t_sheet = source_sheet
                s_mappings = target_mappings
                t_mappings = source_mappings

            similarities_to_save: list[PlagiarismSimilarity] = []
            sheet_similarities: list[float] = []

            # Match question-to-question (equivalent questions only)
            for s_mapping in s_mappings:
                if s_mapping.question_id is None:
                    continue

                # Find the equivalent mapping in target sheet
                t_mapping = next(
                    (tm for tm in t_mappings if tm.question_id == s_mapping.question_id),
                    None
                )
                if not t_mapping:
                    continue

                # Scalability skips:
                # - Text length < 20 chars
                # - Status = NOT_ATTEMPTED
                # - Confidence < 0.50
                if (
                    len(s_mapping.extracted_answer_text.strip()) < 20
                    or s_mapping.status == "NOT_ATTEMPTED"
                    or s_mapping.mapping_confidence < 0.50
                    or len(t_mapping.extracted_answer_text.strip()) < 20
                    or t_mapping.status == "NOT_ATTEMPTED"
                    or t_mapping.mapping_confidence < 0.50
                ):
                    continue

                # Lazy load and cache embeddings
                if s_mapping.id not in embeddings_cache:
                    embeddings_cache[s_mapping.id] = self.plagiarism_score_service.get_embedding(
                        s_mapping.extracted_answer_text
                    )
                if t_mapping.id not in embeddings_cache:
                    embeddings_cache[t_mapping.id] = self.plagiarism_score_service.get_embedding(
                        t_mapping.extracted_answer_text
                    )

                emb1 = embeddings_cache[s_mapping.id]
                emb2 = embeddings_cache[t_mapping.id]

                # Compute similarity scores
                scores = self.plagiarism_score_service.compute_scores(
                    s_mapping.extracted_answer_text,
                    t_mapping.extracted_answer_text,
                    embedding1=emb1,
                    embedding2=emb2
                )

                final_sim = scores["final"]
                sheet_similarities.append(final_sim)

                # Classify question risk level
                # 0.00-0.59 CLEAN, 0.60-0.79 SUSPICIOUS, 0.80-1.00 HIGH_RISK
                if final_sim >= 0.80:
                    q_risk = "HIGH_RISK"
                elif final_sim >= 0.60:
                    q_risk = "SUSPICIOUS"
                else:
                    q_risk = "CLEAN"

                # Normalize source/target mappings (smaller mapping ID is source)
                if s_mapping.id < t_mapping.id:
                    s_map_id, t_map_id = s_mapping.id, t_mapping.id
                else:
                    s_map_id, t_map_id = t_mapping.id, s_mapping.id

                similarity_entity = PlagiarismSimilarity.create(
                    source_answer_sheet_id=s_sheet.id,
                    target_answer_sheet_id=t_sheet.id,
                    source_question_mapping_id=s_map_id,
                    target_question_mapping_id=t_map_id,
                    semantic_similarity=scores["semantic"],
                    lexical_similarity=scores["lexical"],
                    overlap_similarity=scores["overlap"],
                    final_similarity=final_sim,
                    risk_level=q_risk
                )
                similarities_to_save.append(similarity_entity)

            # 5. If we have comparisons, aggregate sheet-level scores
            if sheet_similarities:
                avg_sim = sum(sheet_similarities) / len(sheet_similarities)
                max_sim = max(sheet_similarities)
                exam_highest_similarity = max(exam_highest_similarity, max_sim)

                # Check if highest similarity triggers plagiarism threshold (>= 60% / SUSPICIOUS)
                # We only save plagiarism reports for SUSPICIOUS or HIGH_RISK pairs to avoid DB bloat
                if max_sim >= 0.60:
                    if max_sim >= 0.80:
                        sheet_risk = "HIGH_RISK"
                    else:
                        sheet_risk = "SUSPICIOUS"

                    # Clean up old database records for this specific pair to avoid unique constraint violations
                    # (Deduplication on re-runs)
                    existing_reports = await self.plagiarism_repo.get_sheet_similarity_reports(s_sheet.id)
                    for old_r in existing_reports:
                        if (
                            (old_r.source_answer_sheet_id == s_sheet.id and old_r.target_answer_sheet_id == t_sheet.id)
                            or (old_r.source_answer_sheet_id == t_sheet.id and old_r.target_answer_sheet_id == s_sheet.id)
                        ):
                            # Use custom delete or base delete (delete by ID is inherited)
                            from sqlalchemy import delete
                            from app.infrastructure.persistence.models.plagiarism_report_model import PlagiarismReportModel
                            if hasattr(self.plagiarism_repo, "session"):
                                stmt = delete(PlagiarismReportModel).where(PlagiarismReportModel.id == old_r.id)
                                await self.plagiarism_repo.session.execute(stmt)

                    # Save question-level similarity details
                    for sim in similarities_to_save:
                        # Clean up existing similarity record for these exact mappings first if it exists
                        existing_sims = await self.plagiarism_similarity_repo.list_by_pair(s_sheet.id, t_sheet.id)
                        for old_sim in existing_sims:
                            if (
                                old_sim.source_question_mapping_id == sim.source_question_mapping_id
                                and old_sim.target_question_mapping_id == sim.target_question_mapping_id
                            ):
                                from sqlalchemy import delete
                                from app.infrastructure.persistence.models.plagiarism_similarity_model import PlagiarismSimilarityModel
                                if hasattr(self.plagiarism_similarity_repo, "session"):
                                    stmt = delete(PlagiarismSimilarityModel).where(PlagiarismSimilarityModel.id == old_sim.id)
                                    await self.plagiarism_similarity_repo.session.execute(stmt)

                        await self.plagiarism_similarity_repo.save(sim)

                    # Create details JSON
                    details = {
                        "average_similarity": avg_sim,
                        "compared_questions_count": len(sheet_similarities),
                        "similarities": [
                            {
                                "source_question_mapping_id": str(sim.source_question_mapping_id),
                                "target_question_mapping_id": str(sim.target_question_mapping_id),
                                "final_similarity": sim.final_similarity,
                                "risk_level": sim.risk_level
                            }
                            for sim in similarities_to_save
                        ]
                    }

                    # Create report entity
                    report = PlagiarismReport(
                        exam_id=s_sheet.exam_id,
                        source_answer_sheet_id=s_sheet.id,
                        target_answer_sheet_id=t_sheet.id,
                        similarity_percentage=avg_sim * 100.0,
                        highest_similarity=max_sim,
                        risk_level=sheet_risk,
                        similarity_details=details,
                        flagged_questions=details,
                        status=PlagiarismStatus.DETECTED,
                        id=uuid.uuid4(),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    await self.plagiarism_repo.save(report)
                    created_reports_count += 1

                    # Trigger state protection and notifications if HIGH_RISK
                    if sheet_risk == "HIGH_RISK":
                        # Audit Log: PLAGIARISM_DETECTED
                        audit = AuditLog(
                            action=AuditAction.PLAGIARISM_DETECTED,
                            resource_type="plagiarism_reports",
                            resource_id=report.id,
                            status=AuditStatus.SUCCESS,
                            user_id=user_id,
                            new_values={
                                "source_answer_sheet_id": str(s_sheet.id),
                                "target_answer_sheet_id": str(t_sheet.id),
                                "highest_similarity": max_sim,
                                "risk_level": "HIGH_RISK"
                            }
                        )
                        await self.audit_repo.save(audit)

                        # Flag sheets internally
                        s_sheet.plagiarism_flagged = True
                        t_sheet.plagiarism_flagged = True

                        # Update status for source if not protected
                        if s_sheet.status not in protected_statuses:
                            s_sheet.status = AnswerSheetStatus.PLAGIARISM_REVIEW_PENDING
                        await self.answer_sheet_repo.save(s_sheet)

                        # Update status for target if not protected
                        if t_sheet.status not in protected_statuses:
                            t_sheet.status = AnswerSheetStatus.PLAGIARISM_REVIEW_PENDING
                        await self.answer_sheet_repo.save(t_sheet)

                        # Send notification to exam creator / teacher
                        exam = await self.exam_repo.get_by_id(s_sheet.exam_id)
                        recipient_id = exam.created_by if exam else s_sheet.uploaded_by

                        notification = Notification(
                            user_id=recipient_id,
                            title="High Risk Plagiarism Flagged",
                            message=(
                                f"Answer sheet {s_sheet.original_filename} has been flagged for "
                                f"high plagiarism risk ({max_sim*100:.1f}%) against {t_sheet.original_filename}."
                            ),
                            type=NotificationType.WARNING,
                            category=NotificationCategory.PLAGIARISM_DETECTED.value,
                            resource_type="plagiarism_reports",
                            resource_id=report.id
                        )
                        await self.notification_repo.save(notification)

            if processed_pairs is not None:
                processed_pairs.add((s_id, t_id))

        return {
            "answer_sheet_id": str(answer_sheet_id),
            "compared_sheets": compared_sheets_count,
            "created_reports": created_reports_count,
            "highest_similarity": exam_highest_similarity,
            "status": "COMPLETED"
        }
