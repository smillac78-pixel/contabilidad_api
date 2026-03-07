from functools import lru_cache

from supabase import AsyncClient, acreate_client

from config.settings import get_settings


@lru_cache(maxsize=1)
def _get_settings():
    return get_settings()


async def get_supabase_client() -> AsyncClient:
    settings = _get_settings()
    return await acreate_client(settings.supabase_url, settings.supabase_service_key)
