from uuid import UUID

from supabase import AsyncClient

from domain.entities.family import Family
from domain.repositories.family_repository import FamilyRepository


class SupabaseFamilyRepository(FamilyRepository):
    TABLE = "families"
    USERS_TABLE = "users"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, family: Family) -> Family:
        record = {
            "id": str(family.id),
            "name": family.name,
            "owner_id": str(family.owner_id),
        }
        existing = await self.find_by_id(family.id)
        if existing:
            response = (
                await self._client.table(self.TABLE)
                .update(record)
                .eq("id", str(family.id))
                .execute()
            )
        else:
            response = (
                await self._client.table(self.TABLE)
                .insert(record)
                .execute()
            )
        return await self._to_entity(response.data[0])

    async def find_by_id(self, family_id: UUID) -> Family | None:
        response = (
            await self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(family_id))
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return await self._to_entity(response.data[0])

    async def find_by_owner(self, owner_id: UUID) -> Family | None:
        response = (
            await self._client.table(self.TABLE)
            .select("*")
            .eq("owner_id", str(owner_id))
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return await self._to_entity(response.data[0])

    async def _to_entity(self, record: dict) -> Family:
        # Obtener los miembros de la familia
        members_response = (
            await self._client.table(self.USERS_TABLE)
            .select("id")
            .eq("family_id", record["id"])
            .execute()
        )
        member_ids = [UUID(m["id"]) for m in members_response.data]
        return Family(
            id=UUID(record["id"]),
            name=record["name"],
            owner_id=UUID(record["owner_id"]),
            member_ids=member_ids,
        )
