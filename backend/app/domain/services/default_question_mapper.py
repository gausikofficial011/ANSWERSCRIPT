"""
domain/services/default_question_mapper.py — Default Question Mapper Implementation
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any
import uuid

from app.domain.entities.ocr_result import OCRResult
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.services.question_mapper_interface import QuestionMapper


class DefaultQuestionMapper(QuestionMapper):
    """
    Concrete implementation of QuestionMapper.
    Maps segmented answer texts to exam questions in database, resolving duplicates
    and generating stubs for unanswered (NOT_ATTEMPTED) questions.
    """

    def __init__(self, question_repo: QuestionRepository):
        self.question_repo = question_repo

    async def map_segmented_answers_to_questions(
        self,
        exam_id: uuid.UUID,
        segmented_answers: list[dict[str, Any]],
        ocr_results: list[OCRResult]
    ) -> list[dict[str, Any]]:
        """
        Maps segmented answer blocks to database question IDs.

        Returns:
            List of dictionaries representing mapping results:
            [
                {
                    "question_id": UUID | None,
                    "detected_question_number": int | None,
                    "detected_question_label": str | None,
                    "extracted_answer_text": str,
                    "start_page": int | None,
                    "end_page": int | None,
                    "mapping_confidence": float,
                    "status": str,
                    "duplicate_question_flag": bool,
                    "duplicate_group_id": UUID | None,
                    "source_ocr_result_ids": list[UUID],
                    "source_bounding_boxes": list[dict],
                    "source_page_numbers": list[int],
                    "answer_word_count": int,
                    "answer_character_count": int,
                    "answer_page_count": int
                }
            ]
        """
        # 1. Load database questions for this exam
        questions = await self.question_repo.get_by_exam_id(exam_id)
        questions_by_number = {q.question_number: q for q in questions}

        # 2. Count question number occurrences to detect duplicates
        number_counts = defaultdict(int)
        for seg in segmented_answers:
            num = seg["detected_question_number"]
            if num is not None:
                number_counts[num] += 1

        # Generate unique duplicate group IDs for repeated numbers
        duplicate_group_ids = {}
        for num, count in number_counts.items():
            if count > 1:
                duplicate_group_ids[num] = uuid.uuid4()

        results = []
        mapped_question_ids = set()

        # 3. Process each segmented answer
        for seg in segmented_answers:
            num = seg["detected_question_number"]
            label = seg["detected_question_label"]

            question_id = None
            duplicate_flag = False
            duplicate_group_id = None
            confidence = 0.0
            status = "UNMAPPED"

            # Check if this question number is a duplicate
            if num is not None and num in duplicate_group_ids:
                duplicate_flag = True
                duplicate_group_id = duplicate_group_ids[num]
                status = "DUPLICATE_DETECTED"
                confidence = 0.0  # Confidences are zero for duplicates requiring teacher correction
                if num in questions_by_number:
                    question_id = questions_by_number[num].id
                    mapped_question_ids.add(question_id)
            elif num is not None and num in questions_by_number:
                db_q = questions_by_number[num]
                question_id = db_q.id
                confidence = 1.0  # Exact match
                status = "MAPPED"
                mapped_question_ids.add(db_q.id)
            else:
                status = "UNMAPPED"
                confidence = 0.0

            results.append({
                "question_id": question_id,
                "detected_question_number": num,
                "detected_question_label": label,
                "extracted_answer_text": seg["extracted_answer_text"],
                "start_page": seg["start_page"],
                "end_page": seg["end_page"],
                "mapping_confidence": confidence,
                "status": status,
                "duplicate_question_flag": duplicate_flag,
                "duplicate_group_id": duplicate_group_id,
                "source_ocr_result_ids": seg["source_ocr_result_ids"],
                "source_bounding_boxes": seg["source_bounding_boxes"],
                "source_page_numbers": seg["source_page_numbers"],
                "answer_word_count": seg["answer_word_count"],
                "answer_character_count": seg["answer_character_count"],
                "answer_page_count": seg["answer_page_count"]
            })

        # 4. Generate NOT_ATTEMPTED mappings for unanswered questions
        for q in questions:
            if q.id not in mapped_question_ids:
                # Add unattempted mapping stub
                results.append({
                    "question_id": q.id,
                    "detected_question_number": q.question_number,
                    "detected_question_label": None,
                    "extracted_answer_text": "",
                    "start_page": None,
                    "end_page": None,
                    "mapping_confidence": 0.0,
                    "status": "NOT_ATTEMPTED",
                    "duplicate_question_flag": False,
                    "duplicate_group_id": None,
                    "source_ocr_result_ids": [],
                    "source_bounding_boxes": [],
                    "source_page_numbers": [],
                    "answer_word_count": 0,
                    "answer_character_count": 0,
                    "answer_page_count": 0
                })

        return results
