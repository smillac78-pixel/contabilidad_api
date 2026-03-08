from uuid import UUID

from pydantic import BaseModel, Field


class CreateCategoryRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    icon: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    transaction_type: str = Field(default="expense", pattern=r"^(expense|income)$")


class CategoryResponse(BaseModel):
    id: UUID
    family_id: UUID
    name: str
    icon: str | None
    color: str | None
    is_system: bool
    transaction_type: str = "expense"
