"""
tasks/evaluation_tasks.py — AI Evaluation Celery Task

Handles the asynchronous AI evaluation pipeline for OCR-completed sheets.

Task flow:
  1. Receive answer_sheet_id
  2. Load extracted answers from DB
  3. Load model answers for each question
  4. Load exam scoring config (semantic/keyword weights)
  5. For each question:
     a. Encode student answer → embedding vector
     b. Encode model answer → embedding vector (cached)
     c. Compute cosine similarity
     d. Compute keyword match score
     e. Aggregate weighted score
     f. Generate feedback text
     g. Persist Evaluation record
  6. Update answer sheet status → "evaluated"
  7. Emit EvaluationCompleted event → notify teacher

Queue: evaluation
Max retries: 3
Time limit: 3600s (1 hour for large exams with many questions)
"""

from __future__ import annotations

from celery import Task
from celery.utils.log import get_task_logger

from app.tasks.celery_app import celery_app

logger = get_task_logger(__name__)


class EvaluationTask(Task):
    """
    Base class for the evaluation task.
    Lazy-loads the SentenceTransformer model on first invocation.
    Model is reused across all subsequent task calls in the same worker.
    """

    abstract = True
    _embedder = None

    @property
    def embedder(self):
        if self._embedder is None:
            from app.ai.embeddings.sentence_transformer_embedder import (
                SentenceTransformerEmbedder,
            )
            self._embedder = SentenceTransformerEmbedder()
        return self._embedder


@celery_app.task(
    bind=True,
    base=EvaluationTask,
    name="app.tasks.evaluation_tasks.evaluate_answer_sheet",
    max_retries=3,
    default_retry_delay=30,
    queue="evaluation",
    time_limit=3600,
    soft_time_limit=3300,
)
def evaluate_answer_sheet(
    self: "EvaluationTask",
    answer_sheet_id: str,
    force_reeval: bool = False,
) -> dict:
    """
    Celery task: Run full AI evaluation pipeline for an answer sheet.
    """
    logger.info(
        f"Evaluation task started for answer_sheet_id: {answer_sheet_id}",
        extra={"answer_sheet_id": answer_sheet_id, "task_id": self.request.id},
    )

    import asyncio
    from uuid import UUID
    from app.infrastructure.persistence.database import AsyncSessionLocal
    from app.infrastructure.persistence.repositories import (
        SqlAnswerSheetRepository,
        SqlQuestionMappingRepository,
        SqlAuditLogRepository,
        SqlEvaluationRepository,
        SqlEvaluationRevisionRepository,
        SqlCriterionEvaluationRepository,
        SqlQuestionRepository,
        SqlModelAnswerRepository,
        SqlRubricRepository
    )
    from app.application.use_cases.evaluations.evaluate_answer_use_case import EvaluateAnswerUseCase
    from app.application.use_cases.evaluations.evaluate_answer_sheet_use_case import EvaluateAnswerSheetUseCase

    async def _execute():
        async with AsyncSessionLocal() as session:
            try:
                sheet_id = UUID(answer_sheet_id)
                answer_sheet_repo = SqlAnswerSheetRepository(session)
                question_mapping_repo = SqlQuestionMappingRepository(session)
                audit_repo = SqlAuditLogRepository(session)
                evaluation_repo = SqlEvaluationRepository(session)
                revision_repo = SqlEvaluationRevisionRepository(session)
                criterion_eval_repo = SqlCriterionEvaluationRepository(session)
                question_repo = SqlQuestionRepository(session)
                model_answer_repo = SqlModelAnswerRepository(session)
                rubric_repo = SqlRubricRepository(session)

                evaluate_answer_use_case = EvaluateAnswerUseCase(
                    evaluation_repo=evaluation_repo,
                    revision_repo=revision_repo,
                    criterion_eval_repo=criterion_eval_repo,
                    question_mapping_repo=question_mapping_repo,
                    question_repo=question_repo,
                    model_answer_repo=model_answer_repo,
                    rubric_repo=rubric_repo,
                    audit_repo=audit_repo,
                    embedder=self.embedder
                )

                use_case = EvaluateAnswerSheetUseCase(
                    answer_sheet_repo=answer_sheet_repo,
                    question_mapping_repo=question_mapping_repo,
                    audit_repo=audit_repo,
                    evaluate_answer_use_case=evaluate_answer_use_case
                )

                result = await use_case.execute(sheet_id)
                await session.commit()
                # Trigger plagiarism check asynchronously after successful evaluation
                detect_plagiarism_task.delay(answer_sheet_id)
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Error in evaluation Celery task execution: {str(e)}")
                raise e

    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(_execute())

    except Exception as exc:
        logger.error(f"Evaluation Task failed for sheet {answer_sheet_id}, retrying... Error: {str(exc)}")
        try:
            self.retry(exc=exc)
        except Exception as retry_exc:
            raise retry_exc


@celery_app.task(
    bind=True,
    base=EvaluationTask,
    name="app.tasks.evaluation_tasks.evaluate_exam_batch",
    max_retries=1,
    queue="evaluation",
    time_limit=7200,
)
def evaluate_exam_batch(self: "EvaluationTask", exam_id: str) -> dict:
    """
    Celery task: Trigger evaluation for ALL answer sheets in an exam that are ready.
    """
    logger.info(
        f"Batch evaluation task started for exam_id: {exam_id}",
        extra={"exam_id": exam_id, "task_id": self.request.id},
    )

    import asyncio
    from uuid import UUID
    from sqlalchemy import select
    from app.infrastructure.persistence.database import AsyncSessionLocal
    from app.infrastructure.persistence.models.answer_sheet_model import AnswerSheetModel

    async def _execute():
        async with AsyncSessionLocal() as session:
            exam_uuid = UUID(exam_id)
            # Find all answer sheets for the exam
            query = select(AnswerSheetModel).where(
                AnswerSheetModel.exam_id == exam_uuid,
                AnswerSheetModel.deleted_at.is_(None)
            )
            result = await session.execute(query)
            sheets = result.scalars().all()
            
            sheets_queued = 0
            for sheet in sheets:
                # Trigger evaluate_answer_sheet
                evaluate_answer_sheet.delay(str(sheet.id))
                sheets_queued += 1
                
            return {
                "exam_id": str(exam_uuid),
                "sheets_queued": sheets_queued
            }

    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(_execute())

    except Exception as exc:
        logger.error(f"Batch Evaluation Task failed for exam {exam_id}. Error: {str(exc)}")
        raise exc


@celery_app.task(
    bind=True,
    base=EvaluationTask,
    name="app.tasks.evaluation_tasks.detect_plagiarism_task",
    max_retries=3,
    default_retry_delay=30,
    queue="evaluation",
    time_limit=3600,
)
def detect_plagiarism_task(
    self: "EvaluationTask",
    answer_sheet_id: str,
) -> dict:
    """
    Celery task: Run plagiarism detection for a specific answer sheet.
    """
    logger.info(
        f"Plagiarism detection task started for answer_sheet_id: {answer_sheet_id}",
        extra={"answer_sheet_id": answer_sheet_id, "task_id": self.request.id},
    )

    import asyncio
    from uuid import UUID
    from app.infrastructure.persistence.database import AsyncSessionLocal
    from app.infrastructure.persistence.repositories import (
        SqlAnswerSheetRepository,
        SqlQuestionMappingRepository,
        SqlPlagiarismRepository,
        SqlPlagiarismSimilarityRepository,
        SqlNotificationRepository,
        SqlAuditLogRepository,
        SqlExamRepository
    )
    from app.infrastructure.ai.plagiarism_score_service import PlagiarismScoreService
    from app.application.use_cases.plagiarism.detect_answer_sheet_plagiarism_use_case import DetectAnswerSheetPlagiarismUseCase

    async def _execute():
        async with AsyncSessionLocal() as session:
            try:
                sheet_id = UUID(answer_sheet_id)
                plagiarism_score_service = PlagiarismScoreService(
                    semantic_service=None,  # Will lazy load embedding model in celery worker
                    lexical_service=None,
                    overlap_service=None
                )
                use_case = DetectAnswerSheetPlagiarismUseCase(
                    answer_sheet_repo=SqlAnswerSheetRepository(session),
                    question_mapping_repo=SqlQuestionMappingRepository(session),
                    plagiarism_repo=SqlPlagiarismRepository(session),
                    plagiarism_similarity_repo=SqlPlagiarismSimilarityRepository(session),
                    notification_repo=SqlNotificationRepository(session),
                    audit_repo=SqlAuditLogRepository(session),
                    exam_repo=SqlExamRepository(session),
                    plagiarism_score_service=plagiarism_score_service
                )
                result = await use_case.execute(sheet_id)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Error in plagiarism detection Celery task: {str(e)}")
                raise e

    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(_execute())

    except Exception as exc:
        logger.error(f"Plagiarism detection task failed for sheet {answer_sheet_id}. Error: {str(exc)}")
        try:
            self.retry(exc=exc)
        except Exception as retry_exc:
            raise retry_exc

