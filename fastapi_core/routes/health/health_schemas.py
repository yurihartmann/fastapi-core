from enum import Enum
from typing import List

from pydantic import BaseModel


class StatusReadyEnum(Enum):
    OK = 'OK'
    NOT_OK = 'NOT OK'


class AliveSchema(BaseModel):
    status: str = 'Running'


class DependencyHealthCheckSchema(BaseModel):
    name: str
    ready: bool


class ReadySchema(BaseModel):
    dependencies: List[DependencyHealthCheckSchema]
    status: StatusReadyEnum = StatusReadyEnum.OK.value


class ReadySchemaNotOk(BaseModel):
    dependencies: List[DependencyHealthCheckSchema]
    status: StatusReadyEnum = StatusReadyEnum.NOT_OK.value
