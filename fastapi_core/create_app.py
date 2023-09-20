from enum import Enum

from dependency_injector.containers import Container
from fastapi import APIRouter, FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins import Plugin

from fastapi_core.middleware import AppMiddleware
from fastapi_core.middleware.plugins import HeadersPlugin
from fastapi_core.orchestrators.dependencies_orchestrator import DependenciesOrchestrator
from fastapi_core.routes.health.health_router import health_router
from fastapi_core.routes.migrations.run_migrations_router import run_migrations_router
from fastapi_core.settings import AppSettings
from fastapi_core.utils.app_dependencies_abc import AppDependenciesABC
from fastapi_core.utils.exceptions import InternalErrorSchema


class HelperRoutersEnum(Enum):
    migration = run_migrations_router
    health_check = health_router


def fast_api_create_app(
    app_router: APIRouter,
    title: str = "My App",
    base_path: str = "",
    version: str = "0.1.0",
    container: Container = None,
    helper_routers: tuple[HelperRoutersEnum, ...] = (),
    context_plugins: tuple[Plugin, ...] = (),
    dependencies: tuple[AppDependenciesABC, ...] = (),
) -> FastAPI:
    logger.info(f"Creating FastAPI app ...")
    # Create FastAPI
    app = FastAPI(
        title=title,
        version=version,
        openapi_url=f"{base_path}/openapi.json",
        docs_url=f"{base_path}/docs",
        redoc_url=f"{base_path}/redoc",
    )

    # Redirect in local
    if AppSettings().is_local():
        from fastapi.responses import RedirectResponse

        @app.get(path="/", response_class=RedirectResponse, include_in_schema=False)
        async def redirect():
            return app.docs_url

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
            *context_plugins,
        ),
    )

    # include app_router with response and base path
    app.include_router(
        router=app_router,
        prefix=base_path,
        responses={500: {"model": InternalErrorSchema}},
    )

    # Helper Routers
    for feature in helper_routers:
        app.include_router(router=feature.value, prefix=base_path)

    # Add container in app
    if container:
        app.container = container

    # Register dependencies
    readiness_service = DependenciesOrchestrator()
    for dependency in dependencies:
        readiness_service.add_dependency(dependency)

    return app
