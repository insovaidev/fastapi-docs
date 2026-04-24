import asyncio
import importlib
import pkgutil
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import your project configuration and models
from app.core.config import settings
from app.db import Base
import app.models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Overwrite the sqlalchemy.url with the one from our .env
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the metadata
target_metadata = Base.metadata


def import_all_model_modules() -> None:
    """Load every model module so Base.metadata is fully populated."""
    for _, module_name, _ in pkgutil.iter_modules(app.models.__path__):
        importlib.import_module(f"{app.models.__name__}.{module_name}")


def get_table_filter() -> set[str]:
    """Read optional table filters from `alembic -x table=...`."""
    x_args = context.get_x_argument(as_dictionary=True)
    raw_tables = x_args.get("table", "")
    return {
        table_name.strip()
        for table_name in raw_tables.split(",")
        if table_name.strip()
    }


TARGET_TABLES = get_table_filter()


def get_object_table_name(object_, type_: str) -> str | None:
    if type_ == "table":
        return object_.name

    table = getattr(object_, "table", None)
    if table is not None:
        return table.name

    parent = getattr(object_, "parent", None)
    if parent is not None and getattr(parent, "name", None):
        return parent.name

    return None


def include_object(object_, name, type_, reflected, compare_to):
    if not TARGET_TABLES:
        return True

    table_name = get_object_table_name(object_, type_)
    if table_name is None:
        return True

    return table_name in TARGET_TABLES


import_all_model_modules()

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_object=include_object,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
