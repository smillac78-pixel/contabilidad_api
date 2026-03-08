from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from domain.exceptions import ValidationException
from domain.value_objects.money import Money


@dataclass
class Expense:
    id: UUID
    family_id: UUID
    category_id: UUID
    created_by: UUID
    amount: Money
    description: str
    expense_date: date
    transaction_type: str = "expense"  # "expense" | "income"
    color: str | None = None
    is_recurring: bool = False
    recurring_expense_id: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def validate(self) -> None:
        if self.amount.value <= Decimal(0):
            raise ValidationException("Amount must be positive")
        if self.expense_date > date.today():
            raise ValidationException("Date cannot be in the future")
        if not self.description.strip():
            raise ValidationException("Description is required")
        if self.transaction_type not in ("expense", "income"):
            raise ValidationException("transaction_type must be 'expense' or 'income'")

    def is_editable_by(self, user_id: UUID) -> bool:
        return self.created_by == user_id
