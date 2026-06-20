"""
infrastructure/ocr/image_preprocessor_service.py — Image Preprocessor Service using OpenCV
"""

from __future__ import annotations

import os
from pathlib import Path
import uuid
import cv2
import numpy as np


class ImagePreprocessorService:
    """
    Handles page-wise image preprocessing to optimize text extraction quality for EasyOCR.
    Includes median blur de-noising, CLAHE contrast enhancement, and rotation-based deskewing.
    """

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.processed_images_dir = self.upload_dir / "processed_images"
        self.processed_images_dir.mkdir(parents=True, exist_ok=True)

    def preprocess_image(self, original_image_path: str | Path, answer_sheet_id: uuid.UUID, page_number: int) -> str:
        """
        Executes the preprocessing pipeline on a page image:
        1. Read image in grayscale.
        2. Apply Otsu's thresholding to detect text angle and deskew.
        3. Apply Median Blur to de-noise.
        4. Apply CLAHE to enhance contrast.
        5. Save the preprocessed image.

        Args:
            original_image_path: Path to the original page image.
            answer_sheet_id: UUID of the AnswerSheet.
            page_number: The page number.

        Returns:
            The path to the saved preprocessed image.
        """
        original_image_path = Path(original_image_path)
        if not original_image_path.exists():
            raise FileNotFoundError(f"Original image not found at {original_image_path}")

        # 1. Read image
        img = cv2.imread(str(original_image_path))
        if img is None:
            raise ValueError(f"Could not read image using OpenCV: {original_image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Deskew (using Otsu's binarization-based area rotation angle detection)
        deskewed = self._deskew(gray)

        # 3. Median Blur de-noising
        denoised = cv2.medianBlur(deskewed, 3)

        # 4. CLAHE contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        processed = clahe.apply(denoised)

        # Create output path
        sheet_processed_dir = self.processed_images_dir / str(answer_sheet_id)
        sheet_processed_dir.mkdir(parents=True, exist_ok=True)
        output_path = sheet_processed_dir / f"page_{page_number}.png"

        # Save preprocessed image
        cv2.imwrite(str(output_path), processed)

        return str(output_path)

    def _deskew(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Calculates the skew angle and rotates the image to align it.
        """
        # Threshold the image (invert so text/lines are foreground/white)
        thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Find non-zero coordinates
        pts = cv2.findNonZero(thresh)
        if pts is None:
            return gray_image  # Return original if empty page

        # Calculate bounding box of non-zero pixels
        rect = cv2.minAreaRect(pts)
        angle = rect[-1]

        # OpenCV returns angle between -90 and 0 degrees (or -90 to 90 depending on version)
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        else:
            angle = -angle

        # Cap deskew angle to avoid rotating sideways (only fix minor skews)
        if abs(angle) > 15.0:
            return gray_image

        # Rotate the image
        (h, w) = gray_image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            gray_image,
            M,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

        return rotated
