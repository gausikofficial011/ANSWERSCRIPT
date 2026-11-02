"""
application/use_cases/evaluations/evaluate_answer_use_case.py — Evaluate Answer Use Case
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from app.domain.entities.evaluation import Evaluation
from app.domain.entities.criterion_evaluation import CriterionEvaluation
from app.domain.entities.evaluation_revision import EvaluationRevision
from app.domain.entities.audit_log import AuditLog

from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.domain.repositories.evaluation_revision_repository import EvaluationRevisionRepository
from app.domain.repositories.criterion_evaluation_repository import CriterionEvaluationRepository
from app.domain.repositories.question_mapping_repository import QuestionMappingRepository
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.repositories.model_answer_repository import ModelAnswerRepository
from app.domain.repositories.rubric_repository import RubricRepository
from app.domain.repositories.audit_log_repository import AuditLogRepository

from app.domain.services.rubric_scoring_service import RubricScoringService
from app.infrastructure.ai.semantic_similarity_service import SemanticSimilarityService
from app.infrastructure.ai.keyword_evaluation_service import KeywordEvaluationService
from app.infrastructure.ai.rubric_evaluation_service import RubricEvaluationService
from app.infrastructure.ai.score_aggregation_service import ScoreAggregationService
from app.infrastructure.ai.evaluation_explanation_service import EvaluationExplanationService

from app.core.constants import AuditAction, AuditStatus, GradingMode
from app.domain.exceptions.domain_exception import EntityNotFoundException, BusinessRuleViolationException

logger = logging.getLogger(__name__)


class EvaluateAnswerUseCase:
    """
    Evaluates a student's answer for a single question using AI engines.
    """

    def __init__(
        self,
        evaluation_repo: EvaluationRepository,
        revision_repo: EvaluationRevisionRepository,
        criterion_eval_repo: CriterionEvaluationRepository,
        question_mapping_repo: QuestionMappingRepository,
        question_repo: QuestionRepository,
        model_answer_repo: ModelAnswerRepository,
        rubric_repo: RubricRepository,
        audit_repo: AuditLogRepository,
        semantic_service: SemanticSimilarityService | None = None,
        keyword_service: KeywordEvaluationService | None = None,
        rubric_eval_service: RubricEvaluationService | None = None,
        aggregation_service: ScoreAggregationService | None = None,
        explanation_service: EvaluationExplanationService | None = None,
        embedder: SentenceTransformerEmbedder | None = None,
    ) -> None:
        self.evaluation_repo = evaluation_repo
        self.revision_repo = revision_repo
        self.criterion_eval_repo = criterion_eval_repo
        self.question_mapping_repo = question_mapping_repo
        self.question_repo = question_repo
        self.model_answer_repo = model_answer_repo
        self.rubric_repo = rubric_repo
        self.audit_repo = audit_repo

        self.semantic_service = semantic_service or SemanticSimilarityService(embedder=embedder)
        self.keyword_service = keyword_service or KeywordEvaluationService()
        self.rubric_eval_service = rubric_eval_service or RubricEvaluationService(self.semantic_service, self.keyword_service)
        self.aggregation_service = aggregation_service or ScoreAggregationService()
        self.explanation_service = explanation_service or EvaluationExplanationService()

    async def execute(
        self,
        answer_sheet_id: uuid.UUID,
        question_mapping_id: uuid.UUID,
        user_id: uuid.UUID | None = None
    ) -> Evaluation:
        """
        Executes AI answer scoring, matching criteria and aggregating metrics.
        """
        now = datetime.now(timezone.utc)
        user_id = user_id or uuid.UUID("00000000-0000-0000-0000-000000000000")

        # 1. Fetch mapping
        mapping = await self.question_mapping_repo.get_by_id(question_mapping_id)
        if not mapping:
            raise EntityNotFoundException(entity_type="QuestionMapping", entity_id=question_mapping_id)

        if mapping.question_id is None:
            raise BusinessRuleViolationException(rule="Question mapping must be resolved to a valid question before evaluation.")

        # 2. Fetch question and model answer
        question = await self.question_repo.get_by_id(mapping.question_id)
        if not question:
            raise EntityNotFoundException(entity_type="Question", entity_id=mapping.question_id)

        model_answer = await self.model_answer_repo.get_by_question_id(mapping.question_id)
        if not model_answer:
            raise EntityNotFoundException(entity_type="ModelAnswer", entity_id=mapping.question_id)

        # 3. Fetch active rubric
        rubric = await self.rubric_repo.get_active_by_question_id(mapping.question_id)

        # 4. Check if grading mode is purely manual
        is_manual = rubric and rubric.grading_mode == GradingMode.MANUAL

        # 5. Fetch existing evaluation
        existing_eval = await self.evaluation_repo.get_by_question_id(answer_sheet_id, mapping.question_id)

        # Initial fields setup
        ai_score = 0.0
        similarity_score = 0.0
        keyword_match_score = 0.0
        ai_feedback = ""
        evaluation_confidence = 1.0
        confidence_score = 1.0
        low_confidence_flag = False
        explanation_data = {}
        criterion_details = []

        if mapping.status == "NOT_ATTEMPTED":
            ai_score = 0.0
            similarity_score = 0.0
            keyword_match_score = 0.0
            ai_feedback = "Not attempted."
            evaluation_confidence = 1.0
            confidence_score = 1.0
            low_confidence_flag = False
            explanation_data = {
                "strengths": "N/A",
                "weaknesses": "Question not attempted by the student.",
                "missing_topics": [],
                "improvement_suggestions": "Please attempt all questions.",
                "scoring_reasoning": "0 marks awarded as the question was not attempted."
            }
        elif is_manual:
            # AI evaluation skipped for manual mode
            ai_score = 0.0
            similarity_score = 0.0
            keyword_match_score = 0.0
            ai_feedback = "AI evaluation skipped: Manual grading mode."
            evaluation_confidence = 1.0
            confidence_score = 1.0
            low_confidence_flag = False
            explanation_data = {
                "strengths": "N/A",
                "weaknesses": "Awaiting manual teacher evaluation.",
                "missing_topics": [],
                "improvement_suggestions": "Awaiting manual teacher comments.",
                "scoring_reasoning": "AI scoring bypassed due to Rubric set to MANUAL mode."
            }
        else:
            # Run AI Scorer engines
            # A. Semantic similarity
            similarity_score = self.semantic_service.compute_similarity(
                mapping.extracted_answer_text,
                model_answer.answer_text
            )

            # B. Keywords technical matching
            kw_eval = self.keyword_service.evaluate_keywords(
                mapping.extracted_answer_text,
                model_answer.keywords
            )
            keyword_match_score = kw_eval["keyword_score"]

            # C. Rubric criterion scoring
            rubric_score = None
            if rubric and rubric.criteria:
                # Retrieve weights override if any from question type/scoring configs
                criterion_details = self.rubric_eval_service.evaluate_rubric(
                    mapping.extracted_answer_text,
                    rubric,
                    model_answer.answer_text,
                    question.marks
                )
                # Compute total rubric score
                # Sum of awarded marks across rubric criteria
                rubric_score = sum(cd["awarded_marks"] for cd in criterion_details)

            # D. Aggregation
            agg_results = self.aggregation_service.aggregate_score(
                similarity_score=similarity_score,
                keyword_match_score=keyword_match_score,
                rubric_score=rubric_score,
                max_marks=question.marks
            )

            ai_score = agg_results["final_score"]
            
            # E. Confidence metrics calculation
            # Formulated from mapping confidence, semantic/keyword agreement, and rubric variance
            import math
            divergence = abs(similarity_score - keyword_match_score)
            std_dev = 0.0
            if rubric and rubric.criteria and criterion_details:
                scores = [cd["awarded_marks"] / cd["max_marks"] for cd in criterion_details if cd["max_marks"] > 0]
                if len(scores) > 1:
                    mean = sum(scores) / len(scores)
                    variance = sum((s - mean) ** 2 for s in scores) / (len(scores) - 1)
                    std_dev = math.sqrt(variance)
            
            confidence_val = (
                0.5 * mapping.mapping_confidence +
                0.3 * (1.0 - divergence) -
                0.2 * std_dev
            )
            confidence_score = max(0.0, min(1.0, round(confidence_val, 4)))
            evaluation_confidence = confidence_score
            low_confidence_flag = confidence_score < 0.80

            # F. Explainable AI Feedback
            explanation_data = self.explanation_service.generate_explanation(
                similarity_score=similarity_score,
                matched_keywords=kw_eval["matched_keywords"],
                missing_keywords=kw_eval["missing_keywords"],
                criterion_results=criterion_details if rubric else None,
                max_marks=question.marks,
                final_score=ai_score,
                applied_weights=agg_results["applied_weights"]
            )
            
            ai_feedback = explanation_data["strengths"]

        # 6. Revision logic & Persist
        if existing_eval:
            # Archive existing state into EvaluationRevision
            next_rev = await self.revision_repo.get_next_revision_number(existing_eval.id)
            
            revision = EvaluationRevision(
                id=uuid.uuid4(),
                evaluation_id=existing_eval.id,
                revision_number=next_rev,
                previous_score=existing_eval.final_score,
                new_score=ai_score if existing_eval.teacher_score is None else existing_eval.teacher_score,
                previous_feedback=existing_eval.ai_feedback,
                new_feedback=ai_feedback,
                reason="AI Auto Re-evaluation",
                changed_by=user_id,
                created_at=now,
                updated_at=now
            )
            await self.revision_repo.save(revision)

            # Update existing eval fields
            existing_eval.ai_score = ai_score
            existing_eval.similarity_score = similarity_score
            existing_eval.keyword_match_score = keyword_match_score
            existing_eval.ai_feedback = ai_feedback
            existing_eval.evaluation_confidence = evaluation_confidence
            existing_eval.confidence_score = confidence_score
            existing_eval.low_confidence_flag = low_confidence_flag
            existing_eval.explanation = explanation_data
            existing_eval.updated_at = now
            
            evaluation = await self.evaluation_repo.save(existing_eval)
        else:
            # Create a brand new Evaluation
            evaluation = Evaluation(
                id=uuid.uuid4(),
                answer_sheet_id=answer_sheet_id,
                question_mapping_id=question_mapping_id,
                question_id=mapping.question_id,
                model_answer_id=model_answer.id,
                rubric_id=rubric.id if rubric else None,
                max_marks=question.marks,
                ai_score=ai_score,
                similarity_score=similarity_score,
                keyword_match_score=keyword_match_score,
                ai_feedback=ai_feedback,
                evaluation_confidence=evaluation_confidence,
                confidence_score=confidence_score,
                low_confidence_flag=low_confidence_flag,
                explanation=explanation_data,
                created_at=now,
                updated_at=now
            )
            evaluation = await self.evaluation_repo.save(evaluation)

        # 7. Persist criterion evaluations if rubric is used
        if rubric and rubric.criteria:
            # Delete any previous criterion evaluations for this evaluation to clean up
            # before writing new ones
            existing_crit_evals = await self.criterion_eval_repo.get_by_evaluation_id(evaluation.id)
            for ece in existing_crit_evals:
                await self.criterion_eval_repo.delete(ece.id)

            saved_crit_evals = []
            for cd in criterion_details:
                # If is_manual, scores are None
                ce_ai_score = None if is_manual else cd["ai_score"]
                ce_semantic = None if is_manual else cd["ai_semantic_score"]
                ce_keyword = None if is_manual else cd["ai_keyword_score"]
                ce_feedback = "Manual grading" if is_manual else cd["ai_feedback"]

                ce = CriterionEvaluation(
                    id=uuid.uuid4(),
                    evaluation_id=evaluation.id,
                    rubric_criterion_id=cd["rubric_criterion_id"],
                    ai_score=ce_ai_score,
                    ai_semantic_score=ce_semantic,
                    ai_keyword_score=ce_keyword,
                    ai_feedback=ce_feedback,
                    created_at=now,
                    updated_at=now
                )
                saved_ce = await self.criterion_eval_repo.save(ce)
                saved_crit_evals.append(saved_ce)

        # 8. Log Audit Log
        audit = AuditLog(
            action=AuditAction.EVALUATION_TRIGGERED,
            resource_type="evaluations",
            resource_id=evaluation.id,
            status=AuditStatus.SUCCESS,
            user_id=user_id,
            new_values={"ai_score": ai_score}
        )
        await self.audit_repo.save(audit)

        return evaluation
