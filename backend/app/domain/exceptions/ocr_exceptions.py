"""domain/exceptions/ocr_exceptions.py — OCR Processing Domain Exceptions"""

from app.domain.exceptions.domain_exception import DomainException


class OCRException(DomainException):
    """Base for all OCR subsystem failures visible at the domain level."""


class OCRProcessingException(OCRException):
    """
    Raised when the OCR engine fails to process an image or PDF.

    Args:
        answer_sheet_id: The ID of the failing answer sheet.
        reason:          Technical reason (suitable for logging, not user display).
    """

    def __init__(self, answer_sheet_id: str, reason: str) -> None:
        super().__init__(
            message=f"OCR processing failed for answer sheet '{answer_sheet_id}'.",
            context={"answer_sheet_id": answer_sheet_id, "reason": reason},
        )


class OCRLowConfidenceException(OCRException):
    """
    Raised when extracted text confidence is below the acceptable threshold.
    The answer sheet is flagged for manual review rather than proceeding.
    """

    def __init__(self, answer_sheet_id: str, confidence: float, threshold: float) -> None:
        super().__init__(
            message=(
                f"OCR confidence {confidence:.2f} is below threshold {threshold:.2f} "
                f"for answer sheet '{answer_sheet_id}'. Manual review required."
            ),
            context={
                "answer_sheet_id": answer_sheet_id,
                "confidence": confidence,
                "threshold": threshold,
            },
        )


class QuestionMappingException(OCRException):
    """
    Raised when detected questions cannot be mapped to the exam's
    registered question list with sufficient confidence.
    """

    def __init__(self, answer_sheet_id: str, unmapped_count: int) -> None:
        super().__init__(
            message=(
                f"{unmapped_count} question(s) could not be mapped for "
                f"answer sheet '{answer_sheet_id}'. Manual mapping required."
            ),
            context={
                "answer_sheet_id": answer_sheet_id,
                "unmapped_count": unmapped_count,
            },
        )


class UnsupportedFileFormatException(OCRException):
    """Raised when an uploaded file format is not supported by the OCR pipeline."""

    def __init__(self, filename: str, detected_type: str) -> None:
        super().__init__(
            message=f"File '{filename}' has unsupported format '{detected_type}'.",
            context={"filename": filename, "detected_type": detected_type},
        )
