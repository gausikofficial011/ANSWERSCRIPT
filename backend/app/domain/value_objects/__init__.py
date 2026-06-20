"""
domain/value_objects/__init__.py

Exports all value objects for convenient importing:
  from app.domain.value_objects import Email, Score, SimilarityScore, LanguageCode
"""

from app.domain.value_objects.email import Email
from app.domain.value_objects.language_code import LanguageCode
from app.domain.value_objects.password import Password
from app.domain.value_objects.score import Score, SimilarityScore

__all__ = [
    "Email",
    "LanguageCode",
    "Password",
    "Score",
    "SimilarityScore",
]
