from uuid import uuid4

from application.dto.expense_dto import CreateExpenseInput, ExpenseOutput
from domain.entities.expense import Expense
from domain.exceptions import EntityNotFoundException, UnauthorizedException
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.expense_repository import ExpenseRepository
from domain.repositories.family_repository import FamilyRepository
from domain.value_objects.money import Money


class CreateExpenseUseCase:
    def __init__(
        self,
        expense_repo: ExpenseRepository,
        category_repo: CategoryRepository,
        family_repo: FamilyRepository,
    ) -> None:
        self._expense_repo = expense_repo
        self._category_repo = category_repo
        self._family_repo = family_repo

    async def execute(self, input: CreateExpenseInput) -> ExpenseOutput:
        # 1. Verificar que la familia existe
        family = await self._family_repo.find_by_id(input.family_id)
        if not family:
            raise EntityNotFoundException(f"Family {input.family_id} not found")

        # 2. Verificar que el usuario pertenece a la familia
        if not family.is_member(input.created_by):
            raise UnauthorizedException("User does not belong to this family")

        # 3. Verificar que la categoría existe y pertenece a la familia
        category = await self._category_repo.find_by_id(input.category_id)
        if not category or category.family_id != input.family_id:
            raise EntityNotFoundException(
                f"Category {input.category_id} not found for this family"
            )

        # 4. Construir y validar la entidad de dominio
        expense = Expense(
            id=uuid4(),
            family_id=input.family_id,
            category_id=input.category_id,
            created_by=input.created_by,
            amount=Money(input.amount, input.currency),
            description=input.description,
            expense_date=input.expense_date,
            transaction_type=input.transaction_type,
            color=input.color,
        )
        expense.validate()

        # 5. Persistir
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
            transaction_type=saved.transaction_type,
            color=saved.color,
        )
