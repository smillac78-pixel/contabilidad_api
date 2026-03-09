from uuid import UUID

from domain.exceptions import EntityNotFoundException, UnauthorizedException
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.family_repository import FamilyRepository


class DeleteCategoryUseCase:
    def __init__(
        self,
        category_repo: CategoryRepository,
        family_repo: FamilyRepository,
    ) -> None:
        self._category_repo = category_repo
        self._family_repo = family_repo

    async def execute(self, category_id: UUID, family_id: UUID, requested_by: UUID) -> None:
        family = await self._family_repo.find_by_id(family_id)
        if not family:
            raise EntityNotFoundException(f"Family {family_id} not found")
        if not family.is_member(requested_by):
            raise UnauthorizedException("User does not belong to this family")

        category = await self._category_repo.find_by_id(category_id)
        if not category:
            raise EntityNotFoundException(f"Category {category_id} not found")
        if category.family_id != family_id:
            raise UnauthorizedException("Category does not belong to your family")
        await self._category_repo.delete(category_id)
