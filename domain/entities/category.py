from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.exceptions import DomainException


@dataclass
class Category:
    id: UUID
    family_id: UUID
    name: str
    icon: str | None = None
    color: str | None = None
    is_system: bool = False
    transaction_type: str = "expense"
    created_at: datetime | None = None

    def rename(self, new_name: str) -> None:
        if self.is_system:
            raise DomainException("System categories cannot be renamed")
        if not new_name.strip():
            raise DomainException("Category name cannot be empty")
        self.name = new_name.strip()
