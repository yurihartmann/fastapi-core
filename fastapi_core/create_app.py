from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from dependency_injector.containers import Container
from starlette.responses import JSONResponse
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins import Plugin

from fastapi_core.app_settings import AppSettings
from fastapi_core.middleware import AppMiddleware
from fastapi_core.middleware.plugins import HeadersPlugin
from loguru import logger
from fastapi_core.utils.exceptions import InternalErrorSchema


class Features(BaseModel):
    migration_route: bool = False
    health_route: bool = False

    def init_features(self, app: FastAPI):
        pass
        # if self.migration_route:
        #     app.include_router(migration_router)
        # if self.health_route:
        #     app.include_router(health_router)


class CreateAppConfig(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    title: str = "My App"
    base_path: str = ""
    version: str = "0.1.0"
    container: Container = None
    features: Features = Features()
    context_plugins: tuple[Plugin] = tuple()
    # dependencies: List[ApplicationDependenciesABC] = None,


def fast_api_create_app(
    app_router: APIRouter,
    create_app_config: CreateAppConfig = CreateAppConfig(),
) -> FastAPI:
    logger.info(f"Creating FastAPI app with config {create_app_config}")
    # Create FastAPI
    app = FastAPI(
        title=create_app_config.title,
        version=create_app_config.version,
        openapi_url=f"{create_app_config.base_path}/openapi.json",
        docs_url=f"{create_app_config.base_path}/docs",
        redoc_url=f"{create_app_config.base_path}/redoc",
    )

    # Allow CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add AppMiddleware
    app.add_middleware(AppMiddleware, is_environment_local=AppSettings().is_local())

    # Add AppMiddleware
    app.add_middleware(
        RawContextMiddleware,
        default_error_response=JSONResponse(
            status_code=500,
            content=InternalErrorSchema().dict(),
        ),
        plugins=(
            plugins.RequestIdPlugin(),  # uuid
            plugins.CorrelationIdPlugin(),  # uuid
            HeadersPlugin(),  # Headers global
            *create_app_config.context_plugins,
        ),
    )

    # Init features
    create_app_config.features.init_features(app)

    # include app_router with response and base path
    app.include_router(
        router=app_router, prefix=create_app_config.base_path, responses={500: {"model": InternalErrorSchema}}
    )

    # Add container in app
    if create_app_config.container:
        app.container = create_app_config.container

    # # Register dependencies
    # readiness_service = ReadinessService()
    # for dependency in dependencies if dependencies else []:
    #     readiness_service.add_dependency(dependency)

    return app
