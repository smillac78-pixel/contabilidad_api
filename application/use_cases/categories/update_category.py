from application.dto.category_dto import CategoryOutput, UpdateCategoryInput
from domain.exceptions import EntityNotFoundException, UnauthorizedException
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.family_repository import FamilyRepository


class UpdateCategoryUseCase:
    def __init__(
        self,
        category_repo: CategoryRepository,
        family_repo: FamilyRepository,
    ) -> None:
        self._category_repo = category_repo
        self._family_repo = family_repo

    async def execute(self, input: UpdateCategoryInput) -> CategoryOutput:
        family = await self._family_repo.find_by_id(input.family_id)
        if not family:
            raise EntityNotFoundException(f"Family {input.family_id} not found")
        if not family.is_member(input.requested_by):
            raise UnauthorizedException("User does not belong to this family")

        category = await self._category_repo.find_by_id(input.category_id)
        if not category:
            raise EntityNotFoundException(f"Category {input.category_id} not found")
        if category.family_id != input.family_id:
            raise UnauthorizedException("Category does not belong to this family")

        category.name = input.name.strip()
        category.icon = input.icon
        category.color = input.color
        category.transaction_type = input.transaction_type

        saved = await self._category_repo.save(category)
        return CategoryOutput(
            id=saved.id,
            family_id=saved.family_id,
            name=saved.name,
            icon=saved.icon,
            color=saved.color,
            is_system=saved.is_system,
            transaction_type=saved.transaction_type,
        )
