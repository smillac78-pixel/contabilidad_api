from dataclasses import dataclass
from datetime import date
from uuid import UUID

from application.dto.expense_dto import ExpenseOutput
from domain.exceptions import EntityNotFoundException, UnauthorizedException
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.expense_repository import ExpenseRepository
from domain.repositories.family_repository import FamilyRepository


@dataclass(frozen=True)
class ListExpensesInput:
    family_id: UUID
    requested_by: UUID
    from_date: date | None = None
    to_date: date | None = None
    category_id: UUID | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class ListExpensesOutput:
    items: list[ExpenseOutput]
    total: int
    page: int
    page_size: int
    has_next: bool


class ListExpensesUseCase:
    def __init__(
        self,
        expense_repo: ExpenseRepository,
        category_repo: CategoryRepository,
        family_repo: FamilyRepository,
    ) -> None:
        self._expense_repo = expense_repo
        self._category_repo = category_repo
        self._family_repo = family_repo

    async def execute(self, input: ListExpensesInput) -> ListExpensesOutput:
        # 1. Verificar familia y pertenencia
        family = await self._family_repo.find_by_id(input.family_id)
        if not family:
            raise EntityNotFoundException(f"Family {input.family_id} not found")
        if not family.is_member(input.requested_by):
            raise UnauthorizedException("User does not belong to this family")

        # 2. Cargar categorías para enriquecer la respuesta
        categories = await self._category_repo.find_by_family(input.family_id)
        category_map = {c.id: c.name for c in categories}

        offset = (input.page - 1) * input.page_size

        # 3. Obtener página actual + 1 para saber si hay más
        expenses = await self._expense_repo.find_by_family(
            family_id=input.family_id,
            from_date=input.from_date,
            to_date=input.to_date,
            category_id=input.category_id,
            limit=input.page_size + 1,
            offset=offset,
        )

        has_next = len(expenses) > input.page_size
        items = expenses[: input.page_size]

        return ListExpensesOutput(
            items=[
                ExpenseOutput(
                    id=e.id,
                    family_id=e.family_id,
                    category_id=e.category_id,
                    category_name=category_map.get(e.category_id, "—"),
                    created_by=e.created_by,
                    amount=e.amount.value,
                    currency=e.amount.currency,
                    description=e.description,
                    expense_date=e.expense_date,
                    created_at=e.created_at,
                )
                for e in items
            ],
            total=len(items),
            page=input.page,
            page_size=input.page_size,
            has_next=has_next,
        )
