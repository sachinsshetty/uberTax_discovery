# tenants.py
from sqlalchemy import text
from .database import base_engine, SessionLocalBase

def create_tenant_schema(tenant_schema: str):
    with base_engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {tenant_schema}"))
        # Copy all tables from a template schema (optional)
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {tenant_schema}.legal_persons (LIKE public.legal_persons INCLUDING ALL);
            CREATE TABLE IF NOT EXISTS {tenant_schema}.natural_persons (LIKE public.natural_persons INCLUDING ALL);
            CREATE TABLE IF NOT EXISTS {tenant_schema}.entity_connections (LIKE public.entity_connections INCLUDING ALL);
        """))

def run_migrations_on_tenant(tenant_schema: str):
    # Use Alembic with --sql and target schema
    import subprocess
    subprocess.run([
        "alembic", "upgrade", "head",
        f"--tag={tenant_schema}",
        f"-xschema={tenant_schema}"
    ], check=True)

# tenants.py (small update)
def onboard_new_tenant(tenant_id: str, name: str = None):
    schema_name = f"tenant_{tenant_id}"
    create_tenant_schema(schema_name)
    run_migrations_on_tenant(schema_name)
    
    with SessionLocalBase() as db:
        db.execute(text("""
            INSERT INTO public.tenants (id, schema_name, name)
            VALUES (:id, :schema, :name)
            ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
        """), {"id": tenant_id, "schema": schema_name, "name": name or tenant_id})
        db.commit()