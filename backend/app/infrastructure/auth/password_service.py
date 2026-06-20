"""
infrastructure/auth/password_service.py — Password Hashing Service

Provides utility interfaces to hash passwords and verify plaintext credentials
using the bcrypt algorithm.
"""

from __future__ import annotations

import bcrypt


class PasswordService:
    """
    Service for hashing and verifying passwords using bcrypt.
    """

    @staticmethod
    def hash_password(password: str, rounds: int = 12) -> str:
        """
        Hash a plaintext password using bcrypt.

        Args:
            password: The raw password string.
            rounds: The workload complexity (work factor). Default is 12.

        Returns:
            The salt-hashed string safe for DB persistence.
        """
        # Convert password to bytes
        password_bytes = password.encode("utf-8")
        
        # Generate salt with specified cost factor
        salt = bcrypt.gensalt(rounds=rounds)
        
        # Hash the password
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as decoded string
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plaintext password against a stored bcrypt hash.

        Args:
            plain_password: The raw password guess.
            hashed_password: The stored hash value.

        Returns:
            True if the credentials match, False otherwise.
        """
        try:
            plain_bytes = plain_password.encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(plain_bytes, hashed_bytes)
        except Exception:
            # Handle malformed hashes gracefully (e.g. legacy/invalid string formats)
            return False
