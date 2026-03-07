from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from uuid import UUID

from domain.entities.expense import Expense


class ExpenseRepository(ABC):

    @abstractmethod
    async def save(self, expense: Expense) -> Expense: ...

    @abstractmethod
    async def find_by_id(self, expense_id: UUID) -> Expense | None: ...

    @abstractmethod
    async def find_by_family(
        self,
        family_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
        category_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Expense]: ...

    @abstractmethod
    async def delete(self, expense_id: UUID) -> None: ...

    @abstractmethod
    async def total_by_category(
        self, family_id: UUID, year: int, month: int
    ) -> dict[UUID, Decimal]: ...
