from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from src.config import settings
from src.database import Base
from src.models import Vacancy, PipelineRun  # noqa: F401 — register models

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=settings.db_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(settings.db_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
