from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class CreateExpenseInput:
    family_id: UUID
    category_id: UUID
    created_by: UUID
    amount: Decimal
    currency: str
    description: str
    expense_date: date
    transaction_type: str = "expense"
    color: str | None = None


@dataclass(frozen=True)
class ExpenseOutput:
    id: UUID
    family_id: UUID
    category_id: UUID
    category_name: str
    created_by: UUID
    amount: Decimal
    currency: str
    description: str
    expense_date: date
    created_at: datetime
    transaction_type: str = "expense"
    color: str | None = None
