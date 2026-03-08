from uuid import uuid4

from application.dto.category_dto import CategoryOutput, CreateCategoryInput
from domain.entities.category import Category
from domain.exceptions import DomainException, EntityNotFoundException, UnauthorizedException
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.family_repository import FamilyRepository


class CreateCategoryUseCase:
    def __init__(
        self,
        category_repo: CategoryRepository,
        family_repo: FamilyRepository,
    ) -> None:
        self._category_repo = category_repo
        self._family_repo = family_repo

    async def execute(self, input: CreateCategoryInput) -> CategoryOutput:
        # 1. Verificar familia y pertenencia
        family = await self._family_repo.find_by_id(input.family_id)
        if not family:
            raise EntityNotFoundException(f"Family {input.family_id} not found")
        if not family.is_member(input.created_by):
            raise UnauthorizedException("User does not belong to this family")

        # 2. Verificar nombre único en la familia
        existing = await self._category_repo.find_by_family(input.family_id)
        if any(c.name.lower() == input.name.strip().lower() for c in existing):
            raise DomainException(f"Category '{input.name}' already exists in this family")

        # 3. Crear y persistir
        category = Category(
            id=uuid4(),
            family_id=input.family_id,
            name=input.name.strip(),
            icon=input.icon,
            color=input.color,
            is_system=False,
            transaction_type=input.transaction_type,
        )
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


class ListCategoriesUseCase:
    def __init__(
        self,
        category_repo: CategoryRepository,
        family_repo: FamilyRepository,
    ) -> None:
        self._category_repo = category_repo
        self._family_repo = family_repo

    async def execute(self, family_id, requested_by) -> list[CategoryOutput]:
        family = await self._family_repo.find_by_id(family_id)
        if not family:
            raise EntityNotFoundException(f"Family {family_id} not found")
        if not family.is_member(requested_by):
            raise UnauthorizedException("User does not belong to this family")

        categories = await self._category_repo.find_by_family(family_id)
        return [
            CategoryOutput(
                id=c.id,
                family_id=c.family_id,
                name=c.name,
                icon=c.icon,
                color=c.color,
                is_system=c.is_system,
                transaction_type=c.transaction_type,
            )
            for c in categories
        ]
