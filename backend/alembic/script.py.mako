from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from core.config import settings

data_url = settings.database_url

target_metadata = None

def run_migrations_offline():
    pass

def run_migrations_online():
    pass