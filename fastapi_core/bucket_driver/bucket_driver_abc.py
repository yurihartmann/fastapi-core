from abc import ABC, abstractmethod
from tempfile import TemporaryFile


class BucketDriverABC(ABC):

    @abstractmethod
    async def download_file(self, file_path: str, *args, **kwargs) -> TemporaryFile:
        """Not Implemented"""

    @abstractmethod
    async def upload_file(self, file: bytes, file_path: str, *args, **kwargs):
        """Not Implemented"""
