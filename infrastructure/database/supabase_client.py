from supabase import AsyncClient, acreate_client

from config.settings import get_settings

_client: AsyncClient | None = None


async def get_supabase_client() -> AsyncClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = await acreate_client(settings.supabase_url, settings.supabase_service_key)
    return _client
