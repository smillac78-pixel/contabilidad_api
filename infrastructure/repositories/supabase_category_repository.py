from uuid import UUID

from supabase import AsyncClient

from domain.entities.category import Category
from domain.repositories.category_repository import CategoryRepository


class SupabaseCategoryRepository(CategoryRepository):
    TABLE = "categories"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, category: Category) -> Category:
        record = {
            "id": str(category.id),
            "family_id": str(category.family_id),
            "name": category.name,
            "icon": category.icon,
            "color": category.color,
            "is_system": category.is_system,
            "transaction_type": category.transaction_type,
        }
        existing = await self.find_by_id(category.id)
        if existing:
            response = (
                await self._client.table(self.TABLE)
                .update(record)
                .eq("id", str(category.id))
                .execute()
            )
        else:
            response = (
                await self._client.table(self.TABLE)
                .insert(record)
                .execute()
            )
        return self._to_entity(response.data[0])

    async def find_by_id(self, category_id: UUID) -> Category | None:
        response = (
            await self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(category_id))
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return self._to_entity(response.data[0])

    async def find_by_family(self, family_id: UUID) -> list[Category]:
        response = (
            await self._client.table(self.TABLE)
            .select("*")
            .eq("family_id", str(family_id))
            .order("name")
            .execute()
        )
        return [self._to_entity(r) for r in response.data]

    async def delete(self, category_id: UUID) -> None:
        await (
            self._client.table(self.TABLE)
            .delete()
            .eq("id", str(category_id))
            .execute()
        )

    @staticmethod
    def _to_entity(record: dict) -> Category:
        return Category(
            id=UUID(record["id"]),
            family_id=UUID(record["family_id"]),
            name=record["name"],
            icon=record.get("icon"),
            color=record.get("color"),
            is_system=record.get("is_system", False),
            transaction_type=record.get("transaction_type", "expense"),
        )
