from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from application.dto.expense_dto import CreateExpenseInput
from application.use_cases.expenses.create_expense import CreateExpenseUseCase
from application.use_cases.expenses.delete_expense import DeleteExpenseInput, DeleteExpenseUseCase
from application.use_cases.expenses.list_expenses import ListExpensesInput, ListExpensesUseCase
from domain.exceptions import (
    DomainException,
    EntityNotFoundException,
    UnauthorizedException,
    ValidationException,
)
from presentation.api.schemas.expense_schemas import (
    CreateExpenseRequest,
    ExpenseResponse,
    PaginatedExpensesResponse,
)
from presentation.dependencies import (
    get_create_expense_use_case,
    get_current_family_id,
    get_current_user_row_id,
    get_delete_expense_use_case,
    get_list_expenses_use_case,
)

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo gasto",
)
async def create_expense(
    request: CreateExpenseRequest,
    user_id: UUID = Depends(get_current_user_row_id),
    family_id: UUID = Depends(get_current_family_id),
    use_case: CreateExpenseUseCase = Depends(get_create_expense_use_case),
):
    try:
        result = await use_case.execute(
            CreateExpenseInput(
                family_id=family_id,
                category_id=request.category_id,
                created_by=user_id,
                amount=request.amount,
                currency=request.currency,
                description=request.description,
                expense_date=request.expense_date,
            )
        )
        return ExpenseResponse(**result.__dict__)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except (ValidationException, DomainException) as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "/",
    response_model=PaginatedExpensesResponse,
    summary="Listar gastos de la familia",
)
async def list_expenses(
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    category_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=1000),
    user_id: UUID = Depends(get_current_user_row_id),
    family_id: UUID = Depends(get_current_family_id),
    use_case: ListExpensesUseCase = Depends(get_list_expenses_use_case),
):
    try:
        result = await use_case.execute(
            ListExpensesInput(
                family_id=family_id,
                requested_by=user_id,
                from_date=from_date,
                to_date=to_date,
                category_id=category_id,
                page=page,
                page_size=page_size,
            )
        )
        return PaginatedExpensesResponse(
            items=[ExpenseResponse(**e.__dict__) for e in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            has_next=result.has_next,
        )
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un gasto",
)
async def delete_expense(
    expense_id: UUID,
    user_id: UUID = Depends(get_current_user_row_id),
    use_case: DeleteExpenseUseCase = Depends(get_delete_expense_use_case),
):
    try:
        await use_case.execute(DeleteExpenseInput(expense_id=expense_id, requested_by=user_id))
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
