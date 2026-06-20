"""
domain/services/default_answer_segmenter.py — Default Answer Segmenter Implementation
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.domain.entities.ocr_result import OCRResult
from app.domain.services.answer_segmenter_interface import AnswerSegmenter


class DefaultAnswerSegmenter(AnswerSegmenter):
    """
    Concrete implementation of AnswerSegmenter.
    Groups OCR blocks between sequential question markers to extract multi-page answer segments and evidence.
    """

    async def segment_answers(
        self,
        answer_sheet_id: UUID,
        detected_questions: list[dict[str, Any]],
        ocr_results: list[OCRResult]
    ) -> list[dict[str, Any]]:
        """
        Segments text and evidence for each question.

        Returns:
            List of segmented answers:
            [
                {
                    "detected_question_number": int,
                    "detected_question_label": str,
                    "extracted_answer_text": str,
                    "start_page": int,
                    "end_page": int,
                    "source_ocr_result_ids": list[UUID],
                    "source_bounding_boxes": list[dict],
                    "source_page_numbers": list[int],
                    "answer_word_count": int,
                    "answer_character_count": int,
                    "answer_page_count": int
                }
            ]
        """
        # Flatten all blocks across pages (order matches detector)
        flattened_blocks = []
        for ocr_res in ocr_results:
            page_blocks = sorted(ocr_res.bounding_boxes, key=lambda b: (b.get("y1", 0), b.get("x1", 0)))
            for block in page_blocks:
                flattened_blocks.append({
                    "ocr_result_id": ocr_res.id,
                    "page_number": ocr_res.page_number,
                    "block": block
                })

        # Sort markers by block index
        sorted_markers = sorted(detected_questions, key=lambda m: m["block_index"])
        segmented_answers = []

        total_blocks = len(flattened_blocks)
        for i, marker in enumerate(sorted_markers):
            start_idx = marker["block_index"]
            end_idx = sorted_markers[i + 1]["block_index"] if (i + 1) < len(sorted_markers) else total_blocks

            # Collect blocks in this range
            segment_items = flattened_blocks[start_idx:end_idx]

            # Construct raw texts and clean up the first block's question label
            raw_texts = []
            source_ocr_result_ids = []
            source_bounding_boxes = []
            source_page_numbers = []

            for idx, item in enumerate(segment_items):
                text_val = item["block"].get("text", "")
                
                # For the very first block, strip the question label prefix
                if idx == 0:
                    label = marker["detected_question_label"]
                    if text_val.startswith(label):
                        # Strip label prefix and any separating whitespace/characters
                        text_val = text_val[len(label):].lstrip(".: )-\t")

                raw_texts.append(text_val)
                source_ocr_result_ids.append(item["ocr_result_id"])
                source_bounding_boxes.append(item["block"])
                source_page_numbers.append(item["page_number"])

            # Remove duplicate IDs / page numbers while maintaining order
            unique_ocr_result_ids = list(dict.fromkeys(source_ocr_result_ids))
            unique_page_numbers = sorted(list(set(source_page_numbers)))

            extracted_text = " ".join(raw_texts).strip()

            # Word / Character count metrics
            word_count = len(extracted_text.split()) if extracted_text else 0
            char_count = len(extracted_text)
            page_count = len(unique_page_numbers)

            segmented_answers.append({
                "detected_question_number": marker["detected_question_number"],
                "detected_question_label": marker["detected_question_label"],
                "extracted_answer_text": extracted_text,
                "start_page": unique_page_numbers[0] if unique_page_numbers else marker["page_number"],
                "end_page": unique_page_numbers[-1] if unique_page_numbers else marker["page_number"],
                "source_ocr_result_ids": unique_ocr_result_ids,
                "source_bounding_boxes": source_bounding_boxes,
                "source_page_numbers": unique_page_numbers,
                "answer_word_count": word_count,
                "answer_character_count": char_count,
                "answer_page_count": page_count
            })

        return segmented_answers
