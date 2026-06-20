"""
domain/value_objects/password.py — Password Value Object

Enforces password strength rules at the domain boundary.
Stores only the plaintext for hashing; never persists raw value.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


_MIN_LENGTH = 8
_MAX_LENGTH = 128
_REQUIRES_UPPERCASE = re.compile(r"[A-Z]")
_REQUIRES_LOWERCASE = re.compile(r"[a-z]")
_REQUIRES_DIGIT = re.compile(r"\d")
_REQUIRES_SPECIAL = re.compile(r"[!@#$%^&*()_+\-=\[\]{}|;':\",./<>?]")


@dataclass(frozen=True)
class Password:
    """
    Raw password value object for registration / password change flows.

    Invariants:
      - 8–128 characters
      - At least one uppercase letter
      - At least one lowercase letter
      - At least one digit
      - At least one special character

    IMPORTANT: This object holds the PLAINTEXT password temporarily.
    The Infrastructure layer's PasswordService hashes it before storage.
    Never persist this object's .value field directly.
    """

    value: str

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        errors: list[str] = []

        if len(self.value) < _MIN_LENGTH:
            errors.append(f"Password must be at least {_MIN_LENGTH} characters long.")
        if len(self.value) > _MAX_LENGTH:
            errors.append(f"Password must not exceed {_MAX_LENGTH} characters.")
        if not _REQUIRES_UPPERCASE.search(self.value):
            errors.append("Password must contain at least one uppercase letter.")
        if not _REQUIRES_LOWERCASE.search(self.value):
            errors.append("Password must contain at least one lowercase letter.")
        if not _REQUIRES_DIGIT.search(self.value):
            errors.append("Password must contain at least one digit.")
        if not _REQUIRES_SPECIAL.search(self.value):
            errors.append("Password must contain at least one special character.")

        if errors:
            raise ValueError(" ".join(errors))

    def __repr__(self) -> str:
        # Never expose the raw value in repr/logs
        return "Password('***')"

    def __str__(self) -> str:
        return "***"
