"""
tasks/ocr_tasks.py — OCR Processing Celery Task
"""

from __future__ import annotations

import asyncio
from uuid import UUID
from celery import Task
from celery.utils.log import get_task_logger

from app.tasks.celery_app import celery_app
from app.infrastructure.persistence.database import AsyncSessionLocal
from app.infrastructure.persistence.repositories import (
    SqlAnswerSheetRepository,
    SqlOCRResultRepository,
    SqlAuditLogRepository,
)
from app.infrastructure.ocr.pdf_converter_service import PDFConverterService
from app.infrastructure.ocr.image_preprocessor_service import ImagePreprocessorService
from app.infrastructure.ocr.easyocr_service import EasyOCRService
from app.infrastructure.ocr.ocr_pipeline_service import OCRPipelineService
from app.application.use_cases.ocr.process_answer_sheet_ocr_use_case import ProcessAnswerSheetOCRUseCase

logger = get_task_logger(__name__)


class OCRTask(Task):
    """
    Base class for the OCR task with shared state.
    """
    abstract = True


@celery_app.task(
    bind=True,
    base=OCRTask,
    name="app.tasks.ocr_tasks.process_answer_sheet_ocr",
    max_retries=3,
    default_retry_delay=60,
    queue="ocr",
    time_limit=1800,      # 30-minute hard limit per sheet
    soft_time_limit=1500, # 25-minute soft limit
)
def process_answer_sheet_ocr(
    self: "OCRTask",
    answer_sheet_id: str,
    force_reprocess: bool = False,
) -> dict:
    """
    Celery task: Run full OCR pipeline for an answer sheet.

    Args:
        answer_sheet_id: UUID string of the answer sheet to process.
        force_reprocess: If True, re-run OCR even if already completed.

    Returns:
        Dict with processing summary:
          {"answer_sheet_id": str, "page_count": int, "confidence": float}
    """
    logger.info(
        f"OCR task started for answer_sheet_id: {answer_sheet_id}",
        extra={"answer_sheet_id": answer_sheet_id, "task_id": self.request.id},
    )

    async def _execute():
        from app.infrastructure.persistence.database import get_isolated_session_maker
        session_maker, engine_to_dispose = get_isolated_session_maker()
        try:
            async with session_maker() as session:
                try:
                    sheet_id = UUID(answer_sheet_id)
                    answer_sheet_repo = SqlAnswerSheetRepository(session)
                    ocr_result_repo = SqlOCRResultRepository(session)
                    audit_repo = SqlAuditLogRepository(session)

                    pdf_converter = PDFConverterService()
                    preprocessor = ImagePreprocessorService()
                    ocr_service = EasyOCRService()
                    ocr_pipeline = OCRPipelineService(
                        pdf_converter=pdf_converter,
                        preprocessor=preprocessor,
                        ocr_service=ocr_service
                    )

                    use_case = ProcessAnswerSheetOCRUseCase(
                        answer_sheet_repo=answer_sheet_repo,
                        ocr_result_repo=ocr_result_repo,
                        audit_repo=audit_repo,
                        ocr_pipeline=ocr_pipeline
                    )

                    results = await use_case.execute(sheet_id)
                    await session.commit()

                    # Trigger Question Mapping immediately after OCR completes
                    from app.domain.services.default_question_detector import DefaultQuestionDetector
                    from app.domain.services.default_answer_segmenter import DefaultAnswerSegmenter
                    from app.domain.services.default_question_mapper import DefaultQuestionMapper
                    from app.infrastructure.persistence.repositories import SqlQuestionMappingRepository, SqlQuestionRepository
                    from app.application.use_cases.ocr.process_question_mapping_use_case import ProcessQuestionMappingUseCase

                    question_repo = SqlQuestionRepository(session)
                    question_mapping_repo = SqlQuestionMappingRepository(session)

                    detector = DefaultQuestionDetector()
                    segmenter = DefaultAnswerSegmenter()
                    mapper = DefaultQuestionMapper(question_repo)

                    mapping_use_case = ProcessQuestionMappingUseCase(
                        answer_sheet_repo=answer_sheet_repo,
                        ocr_result_repo=ocr_result_repo,
                        question_mapping_repo=question_mapping_repo,
                        audit_repo=audit_repo,
                        detector=detector,
                        segmenter=segmenter,
                        mapper=mapper
                    )

                    await mapping_use_case.execute(sheet_id)
                    await session.commit()

                    # Trigger AI Evaluation immediately
                    from app.tasks.evaluation_tasks import evaluate_answer_sheet
                    evaluate_answer_sheet.delay(str(sheet_id))

                    # Calculate average confidence
                    avg_conf = sum(r.average_confidence for r in results) / len(results) if results else 1.0

                    return {
                        "answer_sheet_id": str(sheet_id),
                        "page_count": len(results),
                        "confidence": avg_conf
                    }
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Error in OCR Celery task execution: {str(e)}")
                    raise e
        finally:
            await engine_to_dispose.dispose()

    import threading

    def run_coro_safely(coro):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            result = [None]
            exception = [None]
            def _target():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result[0] = new_loop.run_until_complete(coro)
                except Exception as e:
                    exception[0] = e
                finally:
                    new_loop.close()
            t = threading.Thread(target=_target)
            t.start()
            t.join()
            if exception[0] is not None:
                raise exception[0]
            return result[0]
        else:
            return loop.run_until_complete(coro)

    try:
        return run_coro_safely(_execute())
    except Exception as exc:
        logger.error(f"OCR Task failed for sheet {answer_sheet_id}, retrying... Error: {str(exc)}")
        try:
            self.retry(exc=exc)
        except Exception as retry_exc:
            raise retry_exc
