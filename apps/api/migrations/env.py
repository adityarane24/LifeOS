from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import our SQLAlchemy Base.
#
# Base contains the metadata describing our database models.

from app.db.base import Base

# Import all models so SQLAlchemy knows which
# tables our application expects to exist.

from app.models import User
from app.models import Recommendation

# Import application settings.
from app.core.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

config = context.config

# Get custom Alembic command-line arguments.
#
# Example:
# alembic -x db_url="postgresql+psycopg://..." upgrade head
#
# If db_url is provided, Alembic will use that database.
# Otherwise, it will use the application's configured database URL.

x_args = context.get_x_argument(as_dictionary=True)

database_url = x_args.get(
    "db_url",
    settings.database_url,
)

config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%"),
)

# Interpret the config file for Python logging.
# This line sets up loggers basically.

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Tell Alembic which SQLAlchemy metadata to compare
# against the actual PostgreSQL database.

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string
    to the script output.
    """

    url = database_url

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate it with the Alembic context.
    """

    if "db_url" in x_args:
        connectable = create_engine(
            x_args["db_url"],
            poolclass=pool.NullPool,
        )
    else:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()