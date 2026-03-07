from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from domain.exceptions import DomainException


@dataclass
class Family:
    id: UUID
    name: str
    owner_id: UUID
    member_ids: list[UUID] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_member(self, user_id: UUID) -> None:
        if user_id in self.member_ids:
            raise DomainException("User is already a member of this family")
        self.member_ids.append(user_id)

    def remove_member(self, user_id: UUID) -> None:
        if user_id == self.owner_id:
            raise DomainException("Cannot remove the family owner")
        if user_id not in self.member_ids:
            raise DomainException("User is not a member of this family")
        self.member_ids.remove(user_id)

    def is_member(self, user_id: UUID) -> bool:
        return user_id == self.owner_id or user_id in self.member_ids
