from typing import List

from fastapi import APIRouter

from platform_core.services.cache_manager_service import CacheManagerService

cache_router = APIRouter()


@cache_router.get(
    path='/keys',
    description="Get keys in cache for this namespace",
    response_model=List[str]
)
async def get_list_of_keys_in_cache():
    return CacheManagerService().get_keys()


@cache_router.get(
    path='/keys/{key}',
    description="Get value by key in cache for this namespace",
    response_model=dict
)
async def get_value_by_key_in_cache(key: str):
    return {
        key: CacheManagerService().get(key=key)
    }


@cache_router.delete(
    path='/keys/all',
    description="Delete ALL keys in cache for this namespace",
)
async def delete_all_keys_in_cache():
    return CacheManagerService().flush_for_namespace()


@cache_router.delete(
    path='/keys/{key}',
    description="Delete key in cache for this namespace",
)
async def delete_by_key_in_cache(key: str):
    return CacheManagerService().dump(key=key)
