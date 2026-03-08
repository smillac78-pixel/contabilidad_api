from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class UpdateExpenseRequest(BaseModel):
    category_id: UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    description: str = Field(min_length=1, max_length=500)
    expense_date: date
    transaction_type: str = Field(default="expense", pattern=r"^(expense|income)$")
    color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")


class CreateExpenseRequest(BaseModel):
    category_id: UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    description: str = Field(min_length=1, max_length=500)
    expense_date: date
    transaction_type: str = Field(default="expense", pattern=r"^(expense|income)$")
    color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")


class ExpenseResponse(BaseModel):
    id: UUID
    family_id: UUID
    category_id: UUID
    category_name: str
    created_by: UUID
    amount: float
    currency: str
    description: str
    expense_date: date
    created_at: datetime
    transaction_type: str = "expense"
    color: str | None = None


class PaginatedExpensesResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
