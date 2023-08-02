from abc import ABC, abstractmethod


class AppDependenciesABC(ABC):
    @abstractmethod
    async def is_ready(self) -> bool:
        """Not Implemented"""
