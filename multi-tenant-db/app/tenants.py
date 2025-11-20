# app/tenants.py
import logging
import os
from sqlalchemy import text
from alembic.config import Config
from alembic import command
from .database import base_engine, SessionLocalBase

logger = logging.getLogger(__name__)

# This now works because /migrations is copied into the container
MIGRATIONS_DIR = "/migrations"

def create_tenant_schema(tenant_schema: str):
    with base_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {tenant_schema}"))
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {tenant_schema}.legal_persons 
                (LIKE public.legal_persons INCLUDING ALL);
            CREATE TABLE IF NOT EXISTS {tenant_schema}.natural_persons 
                (LIKE public.natural_persons INCLUDING ALL);
            CREATE TABLE IF NOT EXISTS {tenant_schema}.entity_connections 
                (LIKE public.entity_connections INCLUDING ALL);
        """))
        logger.info(f"Schema created and templated: {tenant_schema}")

def run_migrations_on_tenant(tenant_schema: str):
    if not os.path.exists(MIGRATIONS_DIR):
        raise RuntimeError(f"Migrations directory not found at {MIGRATIONS_DIR}")

    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", MIGRATIONS_DIR)
    alembic_cfg.set_main_option("sqlalchemy.url", str(base_engine.url))
    alembic_cfg.attributes["target_schema"] = tenant_schema

    try:
        command.upgrade(alembic_cfg, "head")
        logger.info(f"Migrations applied successfully to {tenant_schema}")
    except Exception as e:
        logger.error(f"Alembic migration failed for {tenant_schema}: {e}")
        raise

def onboard_new_tenant(tenant_id: str, name: str = None):
    schema_name = f"tenant_{tenant_id}"
    create_tenant_schema(schema_name)
    run_migrations_on_tenant(schema_name)

    with SessionLocalBase() as db:
        db.execute(text("""
            INSERT INTO public.tenants (id, schema_name, name, is_active)
            VALUES (:id, :schema, :name, true)
            ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, is_active = true
        """), {"id": tenant_id, "schema": schema_name, "name": name or tenant_id})
        db.commit()

    logger.info(f"Tenant onboarded: {tenant_id} → {schema_name}")