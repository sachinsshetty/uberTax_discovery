# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool, engine_from_config
from alembic import context

# Interpret logging
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

# Import your shared Base
from app.base import Base
target_metadata = Base.metadata

# Get schema passed via config.attributes['target_schema']
schema_name = context.config.attributes.get("target_schema")


def run_migrations_online():
    configuration = context.config.get_section(context.config.config_section)
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=schema_name,
            include_schemas=True,
            compare_type=True,
        )

        with context.begin_transaction():
            if schema_name:
                connection.execute(f"SET search_path TO {schema_name}")
            context.run_migrations()


def run_migrations_offline():
    context.configure(
        url=context.config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        version_table_schema=schema_name,
        literal_binds=True,
    )

    with context.begin_transaction():
        if schema_name:
            context.execute(f"SET search_path TO {schema_name}")
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()