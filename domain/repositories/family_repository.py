from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.family import Family


class FamilyRepository(ABC):

    @abstractmethod
    async def save(self, family: Family) -> Family: ...

    @abstractmethod
    async def find_by_id(self, family_id: UUID) -> Family | None: ...

    @abstractmethod
    async def find_by_owner(self, owner_id: UUID) -> Family | None: ...
