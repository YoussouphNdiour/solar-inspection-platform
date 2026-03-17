"""Configuration Alembic — utilise une connexion synchrone (psycopg2) pour les migrations."""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Base  # noqa: E402
import models  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_url() -> str:
    """Retourne l'URL synchrone (psycopg2) pour Alembic.

    Transforme :
    - postgres://...           → postgresql://...
    - postgresql+asyncpg://... → postgresql://...
    """
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        # Fallback dev local
        from config import settings
        url = settings.database_url

    # Normaliser vers psycopg2 (sync)
    url = url.replace("postgres://", "postgresql://", 1)
    url = url.replace("+asyncpg", "")
    return url


def run_migrations_offline() -> None:
    """Mode offline — génère le SQL sans connexion."""
    context.configure(
        url=get_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Mode online — connexion directe via psycopg2 (synchrone, compatible Alembic)."""
    connectable = create_engine(
        get_sync_url(),
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
