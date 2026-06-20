"""domain/exceptions/evaluation_exceptions.py — AI Evaluation Domain Exceptions"""

from app.domain.exceptions.domain_exception import DomainException


class EvaluationException(DomainException):
    """Base for all evaluation-related domain failures."""


class ModelAnswerMissingException(EvaluationException):
    """
    Raised when an AI evaluation is attempted for a question that
    has no model answer registered.
    """

    def __init__(self, question_id: str) -> None:
        super().__init__(
            message=f"No model answer found for question '{question_id}'. "
                    "Cannot perform AI evaluation.",
            context={"question_id": question_id},
        )


class InvalidScoreException(EvaluationException):
    """
    Raised when a teacher attempts to set a score that violates
    the question's marks boundary.
    """

    def __init__(self, provided: float, max_marks: int) -> None:
        super().__init__(
            message=f"Score {provided} is invalid. Must be between 0 and {max_marks}.",
            context={"provided_score": provided, "max_marks": max_marks},
        )


class EvaluationAlreadyVerifiedException(EvaluationException):
    """
    Raised when attempting to modify an evaluation that has already
    been verified by a teacher (immutable after verification).
    """

    def __init__(self, evaluation_id: str) -> None:
        super().__init__(
            message=f"Evaluation '{evaluation_id}' has already been verified "
                    "and cannot be modified.",
            context={"evaluation_id": evaluation_id},
        )


class ExtractionNotFoundException(EvaluationException):
    """
    Raised when evaluation is triggered but no extracted answer
    is found for a given question.
    """

    def __init__(self, question_id: str, answer_sheet_id: str) -> None:
        super().__init__(
            message=f"No extracted answer found for question '{question_id}' "
                    f"in answer sheet '{answer_sheet_id}'.",
            context={"question_id": question_id, "answer_sheet_id": answer_sheet_id},
        )
