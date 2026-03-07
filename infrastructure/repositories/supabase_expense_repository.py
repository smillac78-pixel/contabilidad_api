from datetime import date
from decimal import Decimal
from uuid import UUID

from supabase import AsyncClient

from domain.entities.expense import Expense
from domain.repositories.expense_repository import ExpenseRepository
from infrastructure.mappers.expense_mapper import ExpenseMapper


class SupabaseExpenseRepository(ExpenseRepository):
    TABLE = "expenses"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, expense: Expense) -> Expense:
        record = ExpenseMapper.to_record(expense)
        existing = await self.find_by_id(expense.id)

        if existing:
            response = (
                await self._client.table(self.TABLE)
                .update(record)
                .eq("id", str(expense.id))
                .execute()
            )
        else:
            response = (
                await self._client.table(self.TABLE)
                .insert(record)
                .execute()
            )

        return ExpenseMapper.to_entity(response.data[0])

    async def find_by_id(self, expense_id: UUID) -> Expense | None:
        response = (
            await self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(expense_id))
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return ExpenseMapper.to_entity(response.data[0])

    async def find_by_family(
        self,
        family_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
        category_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Expense]:
        query = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("family_id", str(family_id))
            .order("expense_date", desc=True)
            .limit(limit)
            .offset(offset)
        )
        if from_date:
            query = query.gte("expense_date", from_date.isoformat())
        if to_date:
            query = query.lte("expense_date", to_date.isoformat())
        if category_id:
            query = query.eq("category_id", str(category_id))

        response = await query.execute()
        return [ExpenseMapper.to_entity(r) for r in response.data]

    async def delete(self, expense_id: UUID) -> None:
        await (
            self._client.table(self.TABLE)
            .delete()
            .eq("id", str(expense_id))
            .execute()
        )

    async def total_by_category(
        self, family_id: UUID, year: int, month: int
    ) -> dict[UUID, Decimal]:
        response = (
            await self._client.table(self.TABLE)
            .select("category_id, amount")
            .eq("family_id", str(family_id))
            .gte("expense_date", f"{year}-{month:02d}-01")
            .lt(
                "expense_date",
                f"{year}-{month % 12 + 1:02d}-01"
                if month < 12
                else f"{year + 1}-01-01",
            )
            .execute()
        )

        totals: dict[UUID, Decimal] = {}
        for row in response.data:
            cat_id = UUID(row["category_id"])
            totals[cat_id] = totals.get(cat_id, Decimal(0)) + Decimal(str(row["amount"]))
        return totals
