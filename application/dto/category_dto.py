from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateCategoryInput:
    family_id: UUID
    created_by: UUID
    name: str
    icon: str | None = None
    color: str | None = None
    transaction_type: str = "expense"


@dataclass(frozen=True)
class CategoryOutput:
    id: UUID
    family_id: UUID
    name: str
    icon: str | None
    color: str | None
    is_system: bool
    transaction_type: str = "expense"
