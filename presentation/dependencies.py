import base64
import json
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from application.use_cases.categories.create_category import CreateCategoryUseCase, ListCategoriesUseCase
from application.use_cases.categories.delete_category import DeleteCategoryUseCase
from application.use_cases.categories.update_category import UpdateCategoryUseCase
from application.use_cases.expenses.create_expense import CreateExpenseUseCase
from application.use_cases.expenses.delete_expense import DeleteExpenseUseCase
from application.use_cases.expenses.list_expenses import ListExpensesUseCase
from application.use_cases.expenses.update_expense import UpdateExpenseUseCase
from infrastructure.database.supabase_client import get_supabase_client
from infrastructure.repositories.supabase_category_repository import SupabaseCategoryRepository
from infrastructure.repositories.supabase_expense_repository import SupabaseExpenseRepository
from infrastructure.repositories.supabase_family_repository import SupabaseFamilyRepository

bearer_scheme = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UUID:
    token = credentials.credentials
    try:
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )


async def get_current_family_id(
    user_id: UUID = Depends(get_current_user_id),
) -> UUID:
    client = await get_supabase_client()
    response = (
        await client.table("users")
        .select("family_id")
        .eq("auth_id", str(user_id))
        .limit(1)
        .execute()
    )
    if not response.data or not response.data[0].get("family_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to a family",
        )
    return UUID(response.data[0]["family_id"])


async def get_current_user_row_id(
    user_id: UUID = Depends(get_current_user_id),
) -> UUID:
    """Returns the users.id (not auth_id) for the current authenticated user."""
    client = await get_supabase_client()
    response = (
        await client.table("users")
        .select("id")
        .eq("auth_id", str(user_id))
        .limit(1)
        .execute()
    )
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User profile not found",
        )
    return UUID(response.data[0]["id"])


# --- Repositorios ---

async def get_expense_repository() -> SupabaseExpenseRepository:
    client = await get_supabase_client()
    return SupabaseExpenseRepository(client)


async def get_category_repository() -> SupabaseCategoryRepository:
    client = await get_supabase_client()
    return SupabaseCategoryRepository(client)


async def get_family_repository() -> SupabaseFamilyRepository:
    client = await get_supabase_client()
    return SupabaseFamilyRepository(client)


# --- Casos de uso: Expenses ---

async def get_create_expense_use_case(
    expense_repo: SupabaseExpenseRepository = Depends(get_expense_repository),
    category_repo: SupabaseCategoryRepository = Depends(get_category_repository),
    family_repo: SupabaseFamilyRepository = Depends(get_family_repository),
) -> CreateExpenseUseCase:
    return CreateExpenseUseCase(expense_repo, category_repo, family_repo)


async def get_list_expenses_use_case(
    expense_repo: SupabaseExpenseRepository = Depends(get_expense_repository),
    category_repo: SupabaseCategoryRepository = Depends(get_category_repository),
    family_repo: SupabaseFamilyRepository = Depends(get_family_repository),
) -> ListExpensesUseCase:
    return ListExpensesUseCase(expense_repo, category_repo, family_repo)


async def get_delete_expense_use_case(
    expense_repo: SupabaseExpenseRepository = Depends(get_expense_repository),
    family_repo: SupabaseFamilyRepository = Depends(get_family_repository),
) -> DeleteExpenseUseCase:
    return DeleteExpenseUseCase(expense_repo, family_repo)


async def get_update_expense_use_case(
    expense_repo: SupabaseExpenseRepository = Depends(get_expense_repository),
    category_repo: SupabaseCategoryRepository = Depends(get_category_repository),
) -> UpdateExpenseUseCase:
    return UpdateExpenseUseCase(expense_repo, category_repo)


# --- Casos de uso: Categories ---

async def get_create_category_use_case(
    category_repo: SupabaseCategoryRepository = Depends(get_category_repository),
    family_repo: SupabaseFamilyRepository = Depends(get_family_repository),
) -> CreateCategoryUseCase:
    return CreateCategoryUseCase(category_repo, family_repo)


async def get_list_categories_use_case(
    category_repo: SupabaseCategoryRepository = Depends(get_category_repository),
    family_repo: SupabaseFamilyRepository = Depends(get_family_repository),
) -> ListCategoriesUseCase:
    return ListCategoriesUseCase(category_repo, family_repo)


async def get_delete_category_use_case(
    category_repo: SupabaseCategoryRepository = Depends(get_category_repository),
    family_repo: SupabaseFamilyRepository = Depends(get_family_repository),
) -> DeleteCategoryUseCase:
    return DeleteCategoryUseCase(category_repo, family_repo)


async def get_update_category_use_case(
    category_repo: SupabaseCategoryRepository = Depends(get_category_repository),
    family_repo: SupabaseFamilyRepository = Depends(get_family_repository),
) -> UpdateCategoryUseCase:
    return UpdateCategoryUseCase(category_repo, family_repo)
