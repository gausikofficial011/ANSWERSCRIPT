"""
domain/value_objects/email.py — Email Value Object

Immutable value object representing a validated email address.
Equality is by value (two Email objects with the same address are equal).
Belongs in domain layer — email format is a business rule.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# RFC 5322 simplified pattern — strict enough for our domain
_EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)


@dataclass(frozen=True)
class Email:
    """
    Validated email address value object.

    Invariants:
      - Must match RFC 5322 simplified format.
      - Stored in lowercase (case-insensitive comparison).
      - Maximum 255 characters.

    Usage:
      email = Email("User@Example.COM")
      str(email)  → "user@example.com"
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        # Bypass frozen restriction to set normalized value
        object.__setattr__(self, "value", normalized)
        self._validate()

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Email address cannot be empty.")
        if len(self.value) > 255:
            raise ValueError("Email address exceeds maximum length of 255 characters.")
        if not _EMAIL_PATTERN.match(self.value):
            raise ValueError(f"'{self.value}' is not a valid email address.")

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Email('{self.value}')"

    @property
    def domain(self) -> str:
        """Return the domain part of the email address."""
        return self.value.split("@")[1]
