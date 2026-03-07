from dataclasses import dataclass
from uuid import UUID

from domain.exceptions import EntityNotFoundException, UnauthorizedException
from domain.repositories.expense_repository import ExpenseRepository
from domain.repositories.family_repository import FamilyRepository


@dataclass(frozen=True)
class DeleteExpenseInput:
    expense_id: UUID
    requested_by: UUID


class DeleteExpenseUseCase:
    def __init__(
        self,
        expense_repo: ExpenseRepository,
        family_repo: FamilyRepository,
    ) -> None:
        self._expense_repo = expense_repo
        self._family_repo = family_repo

    async def execute(self, input: DeleteExpenseInput) -> None:
        # 1. Verificar que el gasto existe
        expense = await self._expense_repo.find_by_id(input.expense_id)
        if not expense:
            raise EntityNotFoundException(f"Expense {input.expense_id} not found")

        # 2. Verificar que el usuario pertenece a la familia del gasto
        family = await self._family_repo.find_by_id(expense.family_id)
        if not family or not family.is_member(input.requested_by):
            raise UnauthorizedException("User does not belong to this family")

        # 3. Solo el creador o el owner de la familia pueden borrar
        if not expense.is_editable_by(input.requested_by) and family.owner_id != input.requested_by:
            raise UnauthorizedException("Only the expense creator or family owner can delete it")

        await self._expense_repo.delete(input.expense_id)
