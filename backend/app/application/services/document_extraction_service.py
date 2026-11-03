"""
backend/app/application/services/document_extraction_service.py

High-performance OCR and PDF text extraction service for question papers,
model answers, and academic documents. Supports digital PDF parsing,
fallback EasyOCR vision recognition for scanned pages, OpenCV image
preprocessing, 2D layout reconstruction, and lexical artifact repair.
"""

from __future__ import annotations

import io
import os
import re
import string
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from app.api.v1.schemas.ocr_schemas import (
    BoundingBoxSchema,
    DocumentExtractionResponse,
    DocumentPageExtractionSchema,
    ExtractedQuestionSchema,
)
from app.infrastructure.ai.text_normalization_service import TextNormalizationService

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing",
    "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
    "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no",
    "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves", "marks", "page", "section", "part", "total", "exam", "subject",
    "university", "institute", "maximum", "time", "hours", "instructions", "answer", "questions", "following"
}


class DocumentExtractionService:
    """
    Advanced Document Extraction Service.
    Coordinates digital PDF text extraction, OpenCV enhancement (deskew, contrast CLAHE, denoise),
    EasyOCR 2D spatial layout reconstruction, and lexical post-processing.
    """

    def __init__(self):
        self._easyocr_service = None
        self._normalizer = TextNormalizationService()

    def _get_ocr_service(self):
        if self._easyocr_service is None:
            from app.infrastructure.ocr.easyocr_service import EasyOCRService
            self._easyocr_service = EasyOCRService()
        return self._easyocr_service

    async def extract_from_file_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str = "application/pdf",
        extract_mode: str = "auto"
    ) -> DocumentExtractionResponse:
        is_pdf = (
            filename.lower().endswith(".pdf")
            or "pdf" in content_type.lower()
        )

        if is_pdf:
            return await self._process_pdf(file_bytes, filename, extract_mode)
        else:
            return await self._process_image(file_bytes, filename)

    async def _process_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        extract_mode: str = "auto"
    ) -> DocumentExtractionResponse:
        import pypdfium2 as pdfium
        from app.infrastructure.ocr.easyocr_service import EasyOCRService

        doc = pdfium.PdfDocument(file_bytes)
        total_pages = len(doc)
        pages_data: list[DocumentPageExtractionSchema] = []
        full_text_list: list[str] = []
        confidences: list[float] = []
        methods_used = set()

        for page_idx in range(total_pages):
            page_num = page_idx + 1
            page = doc[page_idx]

            digital_text = ""
            if extract_mode != "ocr_only":
                try:
                    textpage = page.get_textpage()
                    digital_text = textpage.get_text_range() or ""
                    digital_text = EasyOCRService._clean_and_repair_text(digital_text.strip())
                except Exception:
                    digital_text = ""

            words = digital_text.split()
            if len(words) >= 15 and extract_mode != "ocr_only":
                pages_data.append(
                    DocumentPageExtractionSchema(
                        page_number=page_num,
                        text=digital_text,
                        confidence=0.99,
                        method="digital_pdf",
                        bounding_boxes=[]
                    )
                )
                full_text_list.append(digital_text)
                confidences.append(0.99)
                methods_used.add("digital_pdf")
            else:
                ocr_service = self._get_ocr_service()
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_path = tmp.name

                try:
                    pil_image = page.render(scale=300 / 72).to_pil()
                    pil_image.save(tmp_path, "PNG")

                    enhanced_path = self._enhance_image_cv2(tmp_path)
                    try:
                        ocr_res = ocr_service.extract_text(enhanced_path, page_num)
                    finally:
                        if enhanced_path != tmp_path and os.path.exists(enhanced_path):
                            os.unlink(enhanced_path)
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

                page_text = ocr_res.get("extracted_text", "")
                confidence = float(ocr_res.get("average_confidence", 0.88))
                raw_boxes = ocr_res.get("bounding_boxes", [])

                bboxes = [
                    BoundingBoxSchema(
                        text=b["text"],
                        confidence=b["confidence"],
                        x1=b["x1"],
                        y1=b["y1"],
                        x2=b["x2"],
                        y2=b["y2"],
                        page_number=page_num,
                        low_confidence_flag=b.get("low_confidence_flag", False)
                    )
                    for b in raw_boxes
                ]

                pages_data.append(
                    DocumentPageExtractionSchema(
                        page_number=page_num,
                        text=page_text,
                        confidence=confidence,
                        method="ocr_easyocr_enhanced",
                        bounding_boxes=bboxes
                    )
                )
                full_text_list.append(page_text)
                confidences.append(confidence)
                methods_used.add("ocr_easyocr")

        combined_text = "\n\n".join(full_text_list).strip()
        overall_confidence = sum(confidences) / len(confidences) if confidences else 1.0
        overall_method = " + ".join(sorted(methods_used)) if methods_used else "digital_pdf"

        detected_questions = self._parse_questions(combined_text)
        suggested_keywords = self._extract_keywords(combined_text)
        total_words = len(combined_text.split())

        return DocumentExtractionResponse(
            filename=filename,
            file_type="application/pdf",
            total_pages=total_pages,
            total_words=total_words,
            average_confidence=round(overall_confidence, 4),
            extraction_method=overall_method,
            extracted_full_text=combined_text,
            suggested_keywords=suggested_keywords,
            detected_questions=detected_questions,
            pages=pages_data,
        )

    async def _process_image(
        self,
        file_bytes: bytes,
        filename: str
    ) -> DocumentExtractionResponse:
        ocr_service = self._get_ocr_service()
        suffix = Path(filename).suffix or ".png"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            enhanced_path = self._enhance_image_cv2(tmp_path)
            try:
                ocr_res = ocr_service.extract_text(enhanced_path, page_number=1)
            finally:
                if enhanced_path != tmp_path and os.path.exists(enhanced_path):
                    os.unlink(enhanced_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        extracted_text = ocr_res.get("extracted_text", "")
        confidence = float(ocr_res.get("average_confidence", 0.90))
        raw_boxes = ocr_res.get("bounding_boxes", [])

        bboxes = [
            BoundingBoxSchema(
                text=b["text"],
                confidence=b["confidence"],
                x1=b["x1"],
                y1=b["y1"],
                x2=b["x2"],
                y2=b["y2"],
                page_number=1,
                low_confidence_flag=b.get("low_confidence_flag", False)
            )
            for b in raw_boxes
        ]

        page_data = DocumentPageExtractionSchema(
            page_number=1,
            text=extracted_text,
            confidence=confidence,
            method="ocr_easyocr_enhanced",
            bounding_boxes=bboxes
        )

        detected_questions = self._parse_questions(extracted_text)
        suggested_keywords = self._extract_keywords(extracted_text)
        total_words = len(extracted_text.split())

        return DocumentExtractionResponse(
            filename=filename,
            file_type="image",
            total_pages=1,
            total_words=total_words,
            average_confidence=round(confidence, 4),
            extraction_method="ocr_easyocr_enhanced",
            extracted_full_text=extracted_text,
            suggested_keywords=suggested_keywords,
            detected_questions=detected_questions,
            pages=[page_data],
        )

    def _enhance_image_cv2(self, image_path: str) -> str:
        try:
            img = cv2.imread(image_path)
            if img is None:
                return image_path

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            denoised = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
            clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
            contrast = clahe.apply(denoised)
            deskewed = self._deskew_cv2(contrast)

            enhanced_tmp = tempfile.NamedTemporaryFile(suffix="_enhanced.png", delete=False)
            cv2.imwrite(enhanced_tmp.name, deskewed)
            enhanced_tmp.close()
            return enhanced_tmp.name
        except Exception:
            return image_path

    def _deskew_cv2(self, gray: np.ndarray) -> np.ndarray:
        try:
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            pts = cv2.findNonZero(thresh)
            if pts is None:
                return gray

            rect = cv2.minAreaRect(pts)
            angle = rect[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle

            if abs(angle) > 15.0 or abs(angle) < 0.2:
                return gray

            (h, w) = gray.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        except Exception:
            return gray

    def _parse_questions(self, text: str) -> list[ExtractedQuestionSchema]:
        if not text.strip():
            return []

        pattern = re.compile(
            r'(?:^|\n)\s*(?:(?:Question|Q\.?)\s*(\d+)|\b(\d+)[\.\)])\s*[:\-]?\s*(.*?)(?=(?:\n\s*(?:(?:Question|Q\.?)\s*\d+|\b\d+[\.\)]))|\Z)',
            re.DOTALL | re.IGNORECASE
        )

        matches = list(pattern.finditer(text))
        questions: list[ExtractedQuestionSchema] = []

        if matches:
            for idx, m in enumerate(matches):
                q_num_str = m.group(1) or m.group(2) or str(idx + 1)
                try:
                    q_num = int(q_num_str)
                except ValueError:
                    q_num = idx + 1

                content = m.group(3).strip()
                parsed_q = self._clean_and_structure_question(q_num, content)
                questions.append(parsed_q)
        else:
            paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip().split()) >= 4]
            for idx, p in enumerate(paragraphs[:5]):
                questions.append(self._clean_and_structure_question(idx + 1, p))

        return questions

    def _clean_and_structure_question(self, q_num: int, content: str) -> ExtractedQuestionSchema:
        marks_match = re.search(r'\[?\s*\(?\s*(\d+)\s*(?:marks?|pts?|points?|m)?\s*\)?\s*\]?', content, re.IGNORECASE)
        max_marks = 10
        if marks_match:
            try:
                extracted_marks = int(marks_match.group(1))
                if 1 <= extracted_marks <= 100:
                    max_marks = extracted_marks
            except ValueError:
                pass

        answer_split = re.split(r'(?:Model\s+Answer|Solution|Expected\s+Answer|Ans|Key)\s*[:\-]', content, flags=re.IGNORECASE)
        model_answer = None
        if len(answer_split) > 1:
            q_text = answer_split[0].strip()
            model_answer = answer_split[1].strip()
        else:
            q_text = content.strip()

        q_text = re.sub(r'\[?\s*\(?\s*\d+\s*(?:marks?|pts?|points?|m)?\s*\)?\s*\]?', '', q_text, flags=re.IGNORECASE).strip()
        q_text = re.sub(r'^[:\-\s]+', '', q_text).strip()

        lower_q = q_text.lower()
        if any(term in lower_q for term in ["calculate", "solve", "evaluate", "compute", "derivative", "integral", "matrix", "formula"]):
            q_type = "NUMERICAL"
        elif max_marks <= 3 or len(q_text.split()) < 15 or any(lower_q.startswith(w) for w in ["what is", "define", "state", "name", "list"]):
            q_type = "SHORT_ANSWER"
        else:
            q_type = "ESSAY"

        q_keywords = self._extract_keywords(q_text + " " + (model_answer or ""))

        return ExtractedQuestionSchema(
            question_number=q_num,
            question_text=q_text,
            question_type=q_type,
            max_marks=max_marks,
            suggested_keywords=q_keywords[:10],
            suggested_model_answer=model_answer,
        )

    def _extract_keywords(self, text: str) -> list[str]:
        if not text:
            return []

        words = re.findall(r'\b[A-Za-z][A-Za-z0-9_\-]{2,}\b', text)
        filtered = []
        for w in words:
            low = w.lower()
            if low not in STOPWORDS and len(low) >= 3 and not low.isdigit():
                root = self._normalizer.lemmatize_word(low)
                filtered.append(root if len(root) >= 3 else low)

        if not filtered:
            return []

        counts = Counter(filtered)
        return [w for w, _ in counts.most_common(12)]