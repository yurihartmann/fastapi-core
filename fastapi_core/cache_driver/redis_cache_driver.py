from typing import List, Dict

import redis
from loguru import logger

from fastapi_core.cache_driver.cache_driver_abc import CacheDriverABC
from fastapi_core.utils.app_dependencies_abc import AppDependenciesABC


class RedisCacheDriver(CacheDriverABC, AppDependenciesABC):
    def __init__(
        self, host: str = "localhost", port: int = 6379, password: str | None = None, namespace_prefix: str = ""
    ):
        super().__init__(namespace_prefix=namespace_prefix)
        self.redis = redis.Redis(host=host, port=port, password=password)

    async def is_ready(self) -> bool:
        try:
            self.redis.ping()
            return True
        except Exception:
            return False

    async def keys(self) -> List[str]:
        try:
            return self.redis.keys(pattern=self.namespace_prefix + ":*")

        except Exception as exc:
            logger.error(f"Error in RedisCacheDriver - Error in get keys - Exception = {exc}")
            return []

    async def get(self, key: str) -> bytes | None:
        try:
            return self.redis.get(name=self.get_key_for_namespace(key))
        except Exception as exc:
            logger.error(f"Error in RedisCacheDriver - Error in get value for key={key} - Exception = {exc}")
            return None

    async def get_many(self, keys: List[str]) -> Dict[str, bytes]:
        result_dict = dict()
        try:
            result_list = self.redis.mget(keys=self.get_keys_for_namespace(keys))
            for key, result in zip(keys, result_list):
                if result is not None:
                    result_dict[key] = result
            return result_dict
        except Exception as exc:
            logger.error(f"Error in RedisCacheDriver - Error in get values for keys={keys} - Exception = {exc}")
            return result_dict

    async def set(self, key: str, value, seconds_for_expire: int = 600):
        try:
            self.redis.set(name=self.get_key_for_namespace(key), value=value, ex=seconds_for_expire)
        except Exception as exc:
            logger.error(f"Error in RedisCacheDriver - Error in set key={key} - Exception = {exc}")

    async def set_many(self, mapped_data: Dict[str, str], seconds_for_expire: int = 600) -> None:
        try:
            pipeline = self.redis.pipeline()
            for key, value in mapped_data.items():
                pipeline.set(name=self.get_key_for_namespace(key), value=value, ex=seconds_for_expire)
            pipeline.execute()
        except Exception as exc:
            logger.error(f"Error in RedisCacheDriver - Error in set multiple - Exception = {exc}")

    async def dump(self, key: str):
        try:
            await self.redis.delete(self.get_key_for_namespace(key))
        except Exception as exc:
            logger.error(f"Error in RedisCacheDriver - Error in dump value for key={key} - Exception = {exc}")

    async def dump_prefix(self, key_prefix: str):
        try:
            keys_for_namespace = self.redis.keys(pattern=self.get_key_for_namespace(key_prefix + "*"))

            await self.redis.delete(*keys_for_namespace)
        except Exception as exc:
            logger.error(
                f"Error in RedisCacheDriver - Error in dump values for key_prefix={key_prefix} - Exception = {exc}"
            )

    async def flush_for_namespace(self) -> None:
        try:
            keys_for_namespace = self.redis.keys(pattern=self.namespace_prefix + ":*")

            await self.redis.delete(*keys_for_namespace)

        except Exception as exc:
            logger.error(f"Error in RedisCacheDriver - Error in flush_for_namespace - Exception = {exc}")

    def __str__(self):
        return "RedisCacheDriver"
