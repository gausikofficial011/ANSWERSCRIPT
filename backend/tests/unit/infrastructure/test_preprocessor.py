"""
tests/unit/infrastructure/test_preprocessor.py — Unit Tests for ImagePreprocessorService
"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import uuid
import cv2
import numpy as np
import pytest

from app.infrastructure.ocr.image_preprocessor_service import ImagePreprocessorService


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_preprocess_image_success(temp_dir):
    # 1. Create a dummy original image with some diagonal line skew
    orig_path = temp_dir / "original_page_1.png"
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    # draw a dark text-like rectangle to give Otsu skew detector something to run on
    cv2.rectangle(img, (50, 80), (150, 120), (0, 0, 0), -1)
    cv2.imwrite(str(orig_path), img)

    # 2. Instantiate preprocessor service targeting temp directory
    service = ImagePreprocessorService(upload_dir=str(temp_dir))
    answer_sheet_id = uuid.uuid4()
    
    # 3. Preprocess
    processed_path_str = service.preprocess_image(
        original_image_path=orig_path,
        answer_sheet_id=answer_sheet_id,
        page_number=1
    )

    processed_path = Path(processed_path_str)
    assert processed_path.exists()
    assert "processed_images" in processed_path_str
    assert str(answer_sheet_id) in processed_path_str
    assert "page_1.png" in processed_path_str

    # 4. Verify processed image can be read and is grayscale (1 channel)
    processed_img = cv2.imread(processed_path_str, cv2.IMREAD_GRAYSCALE)
    assert processed_img is not None
    assert processed_img.shape == (200, 200)


def test_preprocess_image_file_not_found(temp_dir):
    service = ImagePreprocessorService(upload_dir=str(temp_dir))
    with pytest.raises(FileNotFoundError):
        service.preprocess_image(
            original_image_path=temp_dir / "does_not_exist.png",
            answer_sheet_id=uuid.uuid4(),
            page_number=1
        )
