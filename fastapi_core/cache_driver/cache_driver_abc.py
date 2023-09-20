import json
from abc import ABC, abstractmethod
from typing import Union, List, Dict

from fastapi_core.utils.app_dependencies_abc import AppDependenciesABC


class CacheDriverABC(AppDependenciesABC, ABC):
    def __init__(self, namespace_prefix: str = ""):
        self.namespace_prefix = namespace_prefix

    def get_key_for_namespace(self, key: str) -> str:
        return self.namespace_prefix + ":" + key

    def get_keys_for_namespace(self, keys: List[str]) -> List[str]:
        keys_with_namespace = []
        for key in keys:
            keys_with_namespace.append(self.get_key_for_namespace(key))
        return keys_with_namespace

    @abstractmethod
    async def keys(self) -> List[str]:
        """Not Implemented"""

    @abstractmethod
    async def get(self, key: str) -> Union[bytes, None]:
        """Not Implemented"""

    async def get_dict(self, key: str) -> dict | None:
        value = await self.get(key=key)

        if value:
            return json.loads(value)

        return value

    @abstractmethod
    async def get_many(self, keys: List[str]) -> Dict[str, bytes]:
        """Not Implemented"""

    @abstractmethod
    async def set(self, key: str, value, seconds_for_expire: int = 600) -> None:
        """Not Implemented"""

    async def set_dict(self, key: str, data: dict, seconds_for_expire: int = 600):
        await self.set(key=key, value=json.dumps(data), seconds_for_expire=seconds_for_expire)

    @abstractmethod
    async def set_many(self, mapped_data: Dict[str, str], seconds_for_expire: int = 600) -> None:
        """Not Implemented"""

    @abstractmethod
    async def dump(self, key: str) -> None:
        """Not Implemented"""

    @abstractmethod
    async def dump_prefix(self, key_prefix: str) -> None:
        """Not Implemented"""

    @abstractmethod
    async def flush_for_namespace(self) -> None:
        """Not Implemented"""
