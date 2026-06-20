"""
infrastructure/ocr/ocr_pipeline_service.py — Coordinates the OCR processing pipeline
"""

from __future__ import annotations

import logging
from pathlib import Path
import uuid

from app.infrastructure.ocr.pdf_converter_service import PDFConverterService
from app.infrastructure.ocr.image_preprocessor_service import ImagePreprocessorService
from app.infrastructure.ocr.easyocr_service import EasyOCRService

logger = logging.getLogger(__name__)


class OCRPipelineService:
    """
    Orchestrator for the OCR ingestion pipeline.
    Runs PDF-to-image conversion, OpenCV enhancement/deskewing, and EasyOCR extraction.
    """

    def __init__(
        self,
        pdf_converter: PDFConverterService,
        preprocessor: ImagePreprocessorService,
        ocr_service: EasyOCRService
    ):
        self.pdf_converter = pdf_converter
        self.preprocessor = preprocessor
        self.ocr_service = ocr_service

    def process_answer_sheet(self, pdf_path: str | Path, answer_sheet_id: uuid.UUID) -> list[dict]:
        """
        Coordinates the ingestion pipeline: PDF -> Page Images -> Processed Images -> OCR text and coordinates.

        Args:
            pdf_path: Local path to the PDF document.
            answer_sheet_id: The UUID of the target AnswerSheet.

        Returns:
            A list of dictionary results, each containing the OCR output for a single page.
        """
        logger.info(f"Starting OCR pipeline for answer sheet {answer_sheet_id} using {pdf_path}")

        # 1. Convert PDF to individual page images (Originals)
        original_image_paths = self.pdf_converter.convert_pdf_to_images(pdf_path, answer_sheet_id)
        page_results = []

        # 2. Loop through pages and preprocess + extract OCR data
        for idx, original_img in enumerate(original_image_paths):
            page_number = idx + 1
            logger.info(f"Processing page {page_number}/{len(original_image_paths)} for sheet {answer_sheet_id}")

            try:
                # Preprocess image (noise reduction, contrast, deskew)
                processed_img = self.preprocessor.preprocess_image(original_img, answer_sheet_id, page_number)

                # Extract text using EasyOCR
                ocr_data = self.ocr_service.extract_text(processed_img, page_number)

                # Add image path details for Review Support
                ocr_data["page_number"] = page_number
                ocr_data["original_image_path"] = str(original_img)
                ocr_data["processed_image_path"] = str(processed_img)

                page_results.append(ocr_data)
            except Exception as e:
                logger.error(f"Failed to process page {page_number} for sheet {answer_sheet_id}: {str(e)}")
                raise e

        logger.info(f"Successfully completed OCR pipeline for answer sheet {answer_sheet_id}. Total pages: {len(page_results)}")
        return page_results
