import asyncio

from fastapi_core.routes.health.health_schemas import DependencyHealthCheckSchema
from fastapi_core.utils import SingletonMeta
from fastapi_core.utils.app_dependencies_abc import AppDependenciesABC


class DependenciesOrchestrator(metaclass=SingletonMeta):
    __dependencies: list[AppDependenciesABC] = []

    def add_dependency(self, dependency: AppDependenciesABC):
        self.__dependencies.append(dependency)

    async def ready(self) -> tuple[bool, list[DependencyHealthCheckSchema]]:
        results: tuple[bool] = await asyncio.gather(*[dependency.is_ready() for dependency in self.__dependencies])

        return all(results), [
            DependencyHealthCheckSchema(name=str(dependency), ready=ready)
            for dependency, ready in zip(self.__dependencies, results)
        ]
