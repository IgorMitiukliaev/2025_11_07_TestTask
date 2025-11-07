# alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from core.config import app_config
from db.session import Base
import models.incident

target_metadata = Base.metadata


# ----- Migration helpers -----
def run_migrations_offline():
    """Run migrations in 'offline' mode (generate SQL without DB)."""
    url = config.get_main_option("sqlalchemy.url") or app_config.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    """Run migrations (sync) using a given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode using an AsyncEngine."""
    # Use the same URL that your app uses
    url = config.get_main_option("sqlalchemy.url") or app_config.DATABASE_URL
    connectable = create_async_engine(url, poolclass=pool.NullPool)

    async with connectable.begin() as async_conn:
        # run the sync migration functions in a sync context
        await async_conn.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
