import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. Add current, parent, and app directories to Python Path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

for p in [PARENT_DIR, os.path.join(PARENT_DIR, "app"), CURRENT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

# 2. Try direct import first, then module fallback
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
try:
    from database import Base
    import models
except ModuleNotFoundError:
    from app.database import Base
    from app import models

config = context.config

if config.config_file_name:
    try:
        fileConfig(config.config_file_name)
    except Exception:
        pass

db_url = os.getenv("DATABASE_URL", "postgresql://microstack:microstack123@db:5432/microstack_db")
config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

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
