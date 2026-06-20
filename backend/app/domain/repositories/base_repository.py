"""
domain/repositories/base_repository.py — Abstract Base Repository

Defines the generic repository interface that all concrete repositories
must implement. Domain layer only depends on this abstraction.

Design:
  - Uses Python's ABC (Abstract Base Class) for interface enforcement.
  - Generic[T] allows type-safe usage: UserRepository extends BaseRepository[User].
  - All methods are async — infrastructure layer uses SQLAlchemy async.
  - Returns domain entities, NOT ORM models.
  - The infrastructure layer handles ORM ↔ Entity mapping.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from app.core.pagination import PaginatedResponse, PaginationParams

# T = Domain Entity type
T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Generic async repository interface.

    All domain repositories extend this class and add
    domain-specific query methods as needed.
    """

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None:
        """
        Retrieve a single entity by its primary key.

        Returns:
            The domain entity, or None if not found.
        """
        ...

    @abstractmethod
    async def get_all(
        self, pagination: PaginationParams
    ) -> PaginatedResponse[T]:
        """
        Retrieve a paginated list of all entities.

        Returns:
            PaginatedResponse containing items and metadata.
        """
        ...

    @abstractmethod
    async def save(self, entity: T) -> T:
        """
        Persist a new or updated entity.

        For new entities, ID generation is the responsibility of the
        domain entity itself (UUID generated at entity creation).

        Returns:
            The persisted entity (with any DB-assigned timestamps).
        """
        ...

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """
        Remove an entity by ID (hard or soft delete depending on entity).

        Returns:
            True if the entity was found and deleted, False otherwise.
        """
        ...

    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        """Check whether an entity with the given ID exists."""
        ...
