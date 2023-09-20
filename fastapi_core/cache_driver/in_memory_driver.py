import dataclasses
import datetime
from typing import Union, List, Dict

from fastapi_core.cache_driver.cache_driver_abc import CacheDriverABC
from fastapi_core.utils.app_dependencies_abc import AppDependenciesABC


@dataclasses.dataclass
class CacheData:
    value: bytes
    seconds_for_expire: int
    datetime: datetime


class InMemoryCacheDriver(CacheDriverABC, AppDependenciesABC):
    async def is_ready(self) -> bool:
        return True

    _memory: dict = {}

    def keys(self) -> List[str]:
        return list(self._memory.keys())

    async def get(self, key: str) -> Union[bytes, None]:
        key = self.get_key_for_namespace(key)
        cache_data: CacheData = self._memory.get(key)

        if not cache_data:
            return None

        if ((cache_data.datetime - datetime.datetime.now()).total_seconds() * -1) > cache_data.seconds_for_expire:
            del self._memory[key]
            return None

        return cache_data.value

    async def get_many(self, keys: List[str]) -> Dict[str, bytes]:
        result_dict = {}
        for key in keys:
            result = await self.get(key)
            if result is not None:
                result_dict[key] = result
        return result_dict

    async def set(self, key: str, value, seconds_for_expire: int = 600) -> None:
        key = self.get_key_for_namespace(key)
        self._memory.update(
            {
                key: CacheData(
                    value=str(value).encode(), seconds_for_expire=seconds_for_expire, datetime=datetime.datetime.now()
                )
            }
        )

    async def set_many(self, mapped_data: Dict[str, str], seconds_for_expire: int = 600) -> None:
        for key, value in mapped_data.items():
            await self.set(key, value, seconds_for_expire)

    async def dump(self, key: str) -> None:
        key = self.get_key_for_namespace(key)
        if self._memory.get(key):
            del self._memory[key]

        return None

    async def dump_prefix(self, key_prefix: str) -> None:
        key_prefix = self.get_key_for_namespace(key_prefix)

        for key in list(self._memory.keys()):
            if key_prefix in key:
                del self._memory[key]

        return None

    async def flush_for_namespace(self) -> None:
        self._memory = {}

    def __str__(self):
        return "InMemoryCacheDriver"
