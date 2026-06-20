"""
tests/unit/application/test_question_mapping.py — Unit Tests for Question Mapping
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.domain.entities.question import Question
from app.domain.repositories.question_repository import QuestionRepository
from app.domain.services.default_question_mapper import DefaultQuestionMapper


@pytest.mark.asyncio
async def test_question_mapping_logic():
    exam_id = uuid.uuid4()
    q1_id = uuid.uuid4()
    q2_id = uuid.uuid4()
    q3_id = uuid.uuid4()

    # Mock questions in database
    db_questions = [
        Question(id=q1_id, exam_id=exam_id, question_number=1, question_text="What is Q1?", marks=10, question_type="short", created_by=uuid.uuid4()),
        Question(id=q2_id, exam_id=exam_id, question_number=2, question_text="What is Q2?", marks=10, question_type="short", created_by=uuid.uuid4()),
        Question(id=q3_id, exam_id=exam_id, question_number=3, question_text="What is Q3?", marks=10, question_type="short", created_by=uuid.uuid4())
    ]

    mock_question_repo = MagicMock(spec=QuestionRepository)
    mock_question_repo.get_by_exam_id = AsyncMock(return_value=db_questions)

    # Segmented answers from OCR
    # Q1 is matched once (direct mapping)
    # Q2 is matched twice (duplicate question detection)
    # Q3 is missing (unanswered question detection)
    segmented = [
        {
            "detected_question_number": 1,
            "detected_question_label": "Q1",
            "extracted_answer_text": "Answer 1",
            "start_page": 1,
            "end_page": 1,
            "source_ocr_result_ids": [uuid.uuid4()],
            "source_bounding_boxes": [],
            "source_page_numbers": [1],
            "answer_word_count": 2,
            "answer_character_count": 8,
            "answer_page_count": 1
        },
        {
            "detected_question_number": 2,
            "detected_question_label": "Q2",
            "extracted_answer_text": "Answer 2 first attempt",
            "start_page": 1,
            "end_page": 2,
            "source_ocr_result_ids": [uuid.uuid4()],
            "source_bounding_boxes": [],
            "source_page_numbers": [1, 2],
            "answer_word_count": 4,
            "answer_character_count": 22,
            "answer_page_count": 2
        },
        {
            "detected_question_number": 2,
            "detected_question_label": "Q2",
            "extracted_answer_text": "Answer 2 duplicate attempt",
            "start_page": 3,
            "end_page": 3,
            "source_ocr_result_ids": [uuid.uuid4()],
            "source_bounding_boxes": [],
            "source_page_numbers": [3],
            "answer_word_count": 4,
            "answer_character_count": 26,
            "answer_page_count": 1
        }
    ]

    mapper = DefaultQuestionMapper(mock_question_repo)
    mappings = await mapper.map_segmented_answers_to_questions(exam_id, segmented, [])

    # We expect:
    # 1. Direct match for Q1 (MAPPED, confidence 1.0)
    # 2. Two duplicate matches for Q2 (DUPLICATE_DETECTED, flag=True, group_id matches, status DUPLICATE_DETECTED, confidence 0.0)
    # 3. One stub match for Q3 (NOT_ATTEMPTED, text="", confidence 0.0)
    assert len(mappings) == 4

    # 1. Q1 mapping
    m1 = next(m for m in mappings if m["detected_question_number"] == 1)
    assert m1["question_id"] == q1_id
    assert m1["status"] == "MAPPED"
    assert m1["mapping_confidence"] == 1.0
    assert m1["duplicate_question_flag"] is False

    # 2. Q2 mappings
    q2_mappings = [m for m in mappings if m["detected_question_number"] == 2]
    assert len(q2_mappings) == 2
    assert q2_mappings[0]["status"] == "DUPLICATE_DETECTED"
    assert q2_mappings[1]["status"] == "DUPLICATE_DETECTED"
    assert q2_mappings[0]["duplicate_question_flag"] is True
    assert q2_mappings[1]["duplicate_question_flag"] is True
    assert q2_mappings[0]["duplicate_group_id"] == q2_mappings[1]["duplicate_group_id"]
    assert q2_mappings[0]["duplicate_group_id"] is not None

    # 3. Q3 mapping
    m3 = next(m for m in mappings if m["detected_question_number"] == 3)
    assert m3["question_id"] == q3_id
    assert m3["status"] == "NOT_ATTEMPTED"
    assert m3["extracted_answer_text"] == ""
    assert m3["mapping_confidence"] == 0.0
