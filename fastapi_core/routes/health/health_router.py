from http import HTTPStatus

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from fastapi_core.orchestrators.dependencies_orchestrator import DependenciesOrchestrator
from fastapi_core.routes.health.health_schemas import AliveSchema, ReadySchema, ReadySchemaNotOk, StatusReadyEnum

health_router = APIRouter()


@health_router.get(
    path='/alive',
    status_code=HTTPStatus.OK,
    response_model=AliveSchema,
    description='Utilizado para checar se o pod subiu'
)
async def health_check_alive():
    return AliveSchema()


@health_router.get(
    path='/ready',
    response_model=ReadySchema,
    responses={
        400: {
            "model": ReadySchemaNotOk
        }
    },
    description='Utilizado para checar se o serviço está pronto para receber conexões'
)
async def health_check_ready():
    all_ready, dependencies = await DependenciesOrchestrator().ready()

    ready_schema = ReadySchema(dependencies=dependencies)

    if not all_ready:
        ready_schema.status = StatusReadyEnum.NOT_OK.value

    return JSONResponse(
        status_code=HTTPStatus.OK if all_ready else HTTPStatus.BAD_REQUEST,
        content=ready_schema.dict()
    )
