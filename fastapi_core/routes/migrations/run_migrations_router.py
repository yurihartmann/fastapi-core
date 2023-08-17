import os

from fastapi import APIRouter

from platform_core.routes.migrations.run_migrations_schemas import RunMigrationsSchema, MIGRATION_ERROR, \
    MIGRATION_SUCCESS, MigrationRollbackDataSchema

run_migrations_router = APIRouter()

MIGRATION_COMMAND = "alembic upgrade head"
ROLLBACK_COMMAND = "alembic downgrade {migration_id}"
CURRENT_COMMAND = "alembic current"


@run_migrations_router.post(
    path='/upgrade',
    response_model=RunMigrationsSchema,
    description=f'Utilizado para rodar migrações - Comando executado: "{MIGRATION_COMMAND}"'
)
async def run_upgrade():
    result = os.system(MIGRATION_COMMAND)

    if os.WEXITSTATUS(result) > 0:
        return RunMigrationsSchema(message=MIGRATION_ERROR)
    else:
        return RunMigrationsSchema(message=MIGRATION_SUCCESS)


@run_migrations_router.post(
    path='/current',
    response_model=RunMigrationsSchema,
    description=f'Ver versão atual - Comando executado: "{CURRENT_COMMAND}"'
)
async def run_current():
    result = os.popen(CURRENT_COMMAND).read()
    return RunMigrationsSchema(message=result)


@run_migrations_router.post(
    path='/rollback',
    response_model=RunMigrationsSchema,
    description=f'Rollback para uma versão especificada - Comando executado: "{ROLLBACK_COMMAND}"'
)
async def run_rollback(payload: MigrationRollbackDataSchema):
    result = os.system(ROLLBACK_COMMAND.replace("{migration_id}", payload.migration_id))

    if os.WEXITSTATUS(result) > 0:
        return RunMigrationsSchema(message=MIGRATION_ERROR)
    else:
        return RunMigrationsSchema(message=MIGRATION_SUCCESS)
