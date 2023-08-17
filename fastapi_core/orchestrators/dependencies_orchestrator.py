import asyncio

from fastapi_core.routes.health.health_schemas import DependencyHealthCheckSchema
from fastapi_core.utils import SingletonMeta
from fastapi_core.utils.app_dependencies_abc import AppDependenciesABC


class DependenciesOrchestrator(metaclass=SingletonMeta):

    __dependencies: list[AppDependenciesABC] = []

    def add_dependency(self, dependency: AppDependenciesABC):
        self.__dependencies.append(dependency)

    async def ready(self) -> tuple[bool, list[DependencyHealthCheckSchema]]:
        is_ready: tuple[int] = await asyncio.gather(
            *[
                dependency.is_ready()
                for dependency in self.__dependencies
            ]
        )

        return all(is_ready), [
            DependencyHealthCheckSchema(
                name=str(dependency),
                ready=is_ready[i]
            )
            for i, dependency in enumerate(self.__dependencies)
        ]
