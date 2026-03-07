from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.category import Category


class CategoryRepository(ABC):

    @abstractmethod
    async def save(self, category: Category) -> Category: ...

    @abstractmethod
    async def find_by_id(self, category_id: UUID) -> Category | None: ...

    @abstractmethod
    async def find_by_family(self, family_id: UUID) -> list[Category]: ...

    @abstractmethod
    async def delete(self, category_id: UUID) -> None: ...
