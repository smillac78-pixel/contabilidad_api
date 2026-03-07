from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from application.dto.expense_dto import CreateExpenseInput
from application.use_cases.expenses.create_expense import CreateExpenseUseCase
from domain.entities.category import Category
from domain.entities.expense import Expense
from domain.entities.family import Family
from domain.exceptions import EntityNotFoundException, UnauthorizedException, ValidationException
from domain.value_objects.money import Money


def make_family(owner_id=None, extra_members=None):
    owner_id = owner_id or uuid4()
    family = Family(id=uuid4(), name="Test Family", owner_id=owner_id)
    for m in (extra_members or []):
        family.add_member(m)
    return family


def make_category(family_id):
    return Category(id=uuid4(), family_id=family_id, name="Agua")


def make_use_case(family=None, category=None, saved_expense=None):
    expense_repo = AsyncMock()
    category_repo = AsyncMock()
    family_repo = AsyncMock()

    family_repo.find_by_id.return_value = family
    category_repo.find_by_id.return_value = category

    if saved_expense:
        expense_repo.save.return_value = saved_expense

    return CreateExpenseUseCase(expense_repo, category_repo, family_repo)


def make_input(family_id, category_id, user_id, expense_date=None):
    return CreateExpenseInput(
        family_id=family_id,
        category_id=category_id,
        created_by=user_id,
        amount=Decimal("50.00"),
        currency="EUR",
        description="Factura agua enero",
        expense_date=expense_date or date.today(),
    )


# ------------------------------------------------------------------ #
# Tests positivos
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_create_expense_returns_output():
    owner_id = uuid4()
    family = make_family(owner_id=owner_id)
    category = make_category(family.id)
    saved = Expense(
        id=uuid4(),
        family_id=family.id,
        category_id=category.id,
        created_by=owner_id,
        amount=Money(Decimal("50.00"), "EUR"),
        description="Factura agua enero",
        expense_date=date.today(),
    )
    use_case = make_use_case(family=family, category=category, saved_expense=saved)
    result = await use_case.execute(make_input(family.id, category.id, owner_id))

    assert result.amount == Decimal("50.00")
    assert result.currency == "EUR"
    assert result.category_name == "Agua"


@pytest.mark.asyncio
async def test_create_expense_allows_family_member():
    owner_id = uuid4()
    member_id = uuid4()
    family = make_family(owner_id=owner_id, extra_members=[member_id])
    category = make_category(family.id)
    saved = Expense(
        id=uuid4(), family_id=family.id, category_id=category.id,
        created_by=member_id, amount=Money(Decimal("30.00"), "EUR"),
        description="Luz", expense_date=date.today(),
    )
    use_case = make_use_case(family=family, category=category, saved_expense=saved)
    result = await use_case.execute(make_input(family.id, category.id, member_id))
    assert result.created_by == member_id


# ------------------------------------------------------------------ #
# Tests de autorización y existencia
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_raises_if_family_not_found():
    use_case = make_use_case(family=None)
    with pytest.raises(EntityNotFoundException, match="Family"):
        await use_case.execute(make_input(uuid4(), uuid4(), uuid4()))


@pytest.mark.asyncio
async def test_raises_if_user_not_in_family():
    family = make_family()
    use_case = make_use_case(family=family, category=None)
    with pytest.raises(UnauthorizedException):
        await use_case.execute(make_input(family.id, uuid4(), uuid4()))


@pytest.mark.asyncio
async def test_raises_if_category_not_found():
    owner_id = uuid4()
    family = make_family(owner_id=owner_id)
    use_case = make_use_case(family=family, category=None)
    with pytest.raises(EntityNotFoundException, match="Category"):
        await use_case.execute(make_input(family.id, uuid4(), owner_id))


@pytest.mark.asyncio
async def test_raises_if_category_belongs_to_another_family():
    owner_id = uuid4()
    family = make_family(owner_id=owner_id)
    other_family_id = uuid4()
    category = make_category(family_id=other_family_id)  # categoría de otra familia

    use_case = make_use_case(family=family, category=category)
    with pytest.raises(EntityNotFoundException, match="Category"):
        await use_case.execute(make_input(family.id, category.id, owner_id))


# ------------------------------------------------------------------ #
# Tests de validación de dominio
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_raises_if_expense_date_in_future():
    from datetime import timedelta
    owner_id = uuid4()
    family = make_family(owner_id=owner_id)
    category = make_category(family.id)
    use_case = make_use_case(family=family, category=category)

    future_date = date.today() + timedelta(days=1)
    with pytest.raises(ValidationException, match="future"):
        await use_case.execute(make_input(family.id, category.id, owner_id, future_date))
