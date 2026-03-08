from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from application.dto.category_dto import CreateCategoryInput
from application.use_cases.categories.create_category import CreateCategoryUseCase, ListCategoriesUseCase
from application.use_cases.categories.delete_category import DeleteCategoryUseCase
from domain.exceptions import DomainException, EntityNotFoundException, UnauthorizedException
from presentation.api.schemas.category_schemas import CategoryResponse, CreateCategoryRequest
from presentation.dependencies import (
    get_create_category_use_case,
    get_current_family_id,
    get_current_user_row_id,
    get_delete_category_use_case,
    get_list_categories_use_case,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría",
)
async def create_category(
    request: CreateCategoryRequest,
    user_id: UUID = Depends(get_current_user_row_id),
    family_id: UUID = Depends(get_current_family_id),
    use_case: CreateCategoryUseCase = Depends(get_create_category_use_case),
):
    try:
        result = await use_case.execute(
            CreateCategoryInput(
                family_id=family_id,
                created_by=user_id,
                name=request.name,
                icon=request.icon,
                color=request.color,
                transaction_type=request.transaction_type,
            )
        )
        return CategoryResponse(**result.__dict__)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "/",
    response_model=list[CategoryResponse],
    summary="Listar categorías de la familia",
)
async def list_categories(
    user_id: UUID = Depends(get_current_user_row_id),
    family_id: UUID = Depends(get_current_family_id),
    use_case: ListCategoriesUseCase = Depends(get_list_categories_use_case),
):
    try:
        results = await use_case.execute(family_id=family_id, requested_by=user_id)
        return [CategoryResponse(**r.__dict__) for r in results]
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una categoría",
)
async def delete_category(
    category_id: UUID,
    user_id: UUID = Depends(get_current_user_row_id),
    family_id: UUID = Depends(get_current_family_id),
    use_case: DeleteCategoryUseCase = Depends(get_delete_category_use_case),
):
    try:
        await use_case.execute(
            category_id=category_id,
            family_id=family_id,
            requested_by=user_id,
        )
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))
