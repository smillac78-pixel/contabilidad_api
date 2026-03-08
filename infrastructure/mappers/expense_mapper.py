from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from domain.entities.expense import Expense
from domain.value_objects.money import Money


class ExpenseMapper:

    @staticmethod
    def to_entity(record: dict) -> Expense:
        return Expense(
            id=UUID(record["id"]),
            family_id=UUID(record["family_id"]),
            category_id=UUID(record["category_id"]),
            created_by=UUID(record["created_by"]),
            amount=Money(Decimal(str(record["amount"])), record["currency"]),
            description=record["description"],
            expense_date=date.fromisoformat(record["expense_date"]),
            transaction_type=record.get("transaction_type", "expense"),
            color=record.get("color"),
            is_recurring=record.get("is_recurring", False),
            recurring_expense_id=(
                UUID(record["recurring_expense_id"])
                if record.get("recurring_expense_id")
                else None
            ),
            created_at=datetime.fromisoformat(record["created_at"]),
            updated_at=datetime.fromisoformat(record["updated_at"]),
        )

    @staticmethod
    def to_record(expense: Expense) -> dict:
        record: dict = {
            "id": str(expense.id),
            "family_id": str(expense.family_id),
            "category_id": str(expense.category_id),
            "created_by": str(expense.created_by),
            "amount": float(expense.amount.value),
            "currency": expense.amount.currency,
            "description": expense.description,
            "expense_date": expense.expense_date.isoformat(),
            "transaction_type": expense.transaction_type,
            "color": expense.color,
            "is_recurring": expense.is_recurring,
            "recurring_expense_id": (
                str(expense.recurring_expense_id)
                if expense.recurring_expense_id
                else None
            ),
        }
        return record
