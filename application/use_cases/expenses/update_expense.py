from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from application.dto.expense_dto import ExpenseOutput
from domain.exceptions import EntityNotFoundException, UnauthorizedException, ValidationException
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.expense_repository import ExpenseRepository
from domain.value_objects.money import Money


@dataclass(frozen=True)
class UpdateExpenseInput:
    expense_id: UUID
    requested_by: UUID
    family_id: UUID
    category_id: UUID
    amount: Decimal
    currency: str
    description: str
    expense_date: date


class UpdateExpenseUseCase:
    def __init__(
        self,
        expense_repo: ExpenseRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self._expense_repo = expense_repo
        self._category_repo = category_repo

    async def execute(self, input: UpdateExpenseInput) -> ExpenseOutput:
        expense = await self._expense_repo.find_by_id(input.expense_id)
        if not expense:
            raise EntityNotFoundException(f"Expense {input.expense_id} not found")

        if not expense.is_editable_by(input.requested_by):
            raise UnauthorizedException("Only the creator can edit this expense")

        category = await self._category_repo.find_by_id(input.category_id)
        if not category or category.family_id != input.family_id:
            raise EntityNotFoundException(f"Category {input.category_id} not found for this family")

        expense.amount = Money(input.amount, input.currency)
        expense.category_id = input.category_id
        expense.description = input.description
        expense.expense_date = input.expense_date
        expense.validate()

        saved = await self._expense_repo.save(expense)

        return ExpenseOutput(
            id=saved.id,
            family_id=saved.family_id,
            category_id=saved.category_id,
            category_name=category.name,
            created_by=saved.created_by,
            amount=saved.amount.value,
            currency=saved.amount.currency,
            description=saved.description,
            expense_date=saved.expense_date,
            created_at=saved.created_at,
        )
