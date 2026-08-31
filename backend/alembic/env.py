from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import make_url
import ssl

from alembic import context
from app.core.database import Base
import app.models  # noqa: F401 - ensure all models are registered
from app.core.config import settings as app_settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _create_connectable():
    url = make_url(app_settings.DATABASE_URL)
    # Convert asyncpg dialect to psycopg2 for sync migrations
    if url.drivername == "postgresql+asyncpg":
        url = url.set(drivername="postgresql+psycopg2")
    query = dict(url.query)
    connect_args = {}

    # psycopg2 uses sslmode in URL; asyncpg uses ssl connect_arg
    # For psycopg2, keep sslmode in the URL
    if url.drivername == "postgresql+psycopg2":
        if query.get("sslmode") in ("require", "verify-ca", "verify-full"):
            # sslmode is already in the URL query, just keep it
            pass
    else:
        # For other dialects, use connect_args
        if query.get("sslmode") in ("require", "verify-ca", "verify-full"):
            ssl_ctx = ssl.create_default_context()
            if query.get("sslmode") == "require":
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ssl_ctx

    # Remove query params that aren't standard for the driver
    if url.drivername == "postgresql+psycopg2":
        # Keep sslmode, remove channel_binding
        query = {k: v for k, v in query.items() if k != "channel_binding"}
        url = url.set(query=query)
    else:
        url = url.set(query={})

    return create_engine(
        url,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )


def run_migrations_offline() -> None:
    url = app_settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = _create_connectable()

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
