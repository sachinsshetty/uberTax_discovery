Here’s a production-grade, battle-tested way to implement **multi-tenant (100+ tenants)** architecture on top of your current registry application (FastAPI + SQLAlchemy 2.0 + PostgreSQL) while keeping performance, security, and simplicity under control.

### Recommended Approach for 100–500+ tenants: **Schema-based multi-tenancy** (Separate PostgreSQL schema per tenant)

This is the sweet spot for your use case: strong data isolation, good performance, easy backups per tenant, and still manageable migration tooling.

#### Why schema-based over other options?

| Approach                  | Isolation | Performance | Migration ease | Complexity | Verdict for 100+ tenants |
|---------------------------|----------|-------------|----------------|------------|--------------------------|
| Shared table + tenant_id  | Low      | Best        | Easy           | Low        | Risky (data leaks)       |
| Separate database per tenant | Perfect | Good        | Hard           | Very high  | Overkill & expensive     |
| **Separate schema per tenant** | **Perfect** | **Very good** | Manageable     | Medium     | **Recommended**          |

#### 1. Updated database.py (tenant-aware engine & session)

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic_settings import BaseSettings
from contextvars import ContextVar
from typing import Generator
import threading

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/registry"
    class Config:
        env_file = ".env"

settings = Settings()

# Thread-local storage for current tenant schema
_current_tenant: ContextVar[str | None] = ContextVar("current_tenant", default=None)

# Base engine connected to the "public" schema (used for tenant management)
base_engine = create_engine(settings.DATABASE_URL, isolation_level="AUTOCOMMIT")
SessionLocalBase = sessionmaker(bind=base_engine)

# Tenant-specific engines cache (one engine per schema)
_engines_cache: dict[str, any] = {}
_engines_lock = threading.Lock()

def get_tenant_engine(tenant_schema: str):
    if tenant_schema in _engines_cache:
        return _engines_cache[tenant_schema]
    
    with _engines_lock:
        if tenant_schema not in _engines_cache:
            tenant_url = f"{settings.DATABASE_URL.rstrip('/')}/{tenant_schema}"
            engine = create_engine(
                tenant_url,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                connect_args={"options": f"-csearch_path={tenant_schema}"}
            )
            _engines_cache[tenant_schema] = engine
    return _engines_cache[tenant_schema]

def get_db() -> Generator[Session, None, None]:
    tenant_schema = _current_tenant.get()
    if not tenant_schema:
        raise ValueError("No tenant context set. Use tenant_context()")

    engine = get_tenant_engine(tenant_schema)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Context manager to set current tenant
from contextlib import contextmanager

@contextmanager
def tenant_context(schema: str):
    token = _current_tenant.set(schema)
    try:
        yield
    finally:
        _current_tenant.reset(token)
```

#### 2. Tenant management functions (create/drop schemas + migrations)

```python
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

def onboard_new_tenant(tenant_id: str):
    schema_name = f"tenant_{tenant_id}"
    create_tenant_schema(schema_name)
    run_migrations_on_tenant(schema_name)
    # Also insert tenant metadata into a public.tenants table
    with SessionLocalBase() as db:
        db.execute(text("""
            INSERT INTO public.tenants (id, schema_name, name, created_at)
            VALUES (:id, :schema, :name, NOW())
            ON CONFLICT (id) DO NOTHING
        """), {"id": tenant_id, "schema": schema_name, "name": tenant_id})
        db.commit()
```

#### 3. FastAPI middleware to set tenant context automatically

```python
# middleware.py
from fastapi import Request, HTTPException
from .database import tenant_context
import re

async def tenant_middleware(request: Request, call_next):
    host = request.headers.get("host", "")
    subdomain = host.split(".")[0]  # e.g. acme.example.com → acme

    # Or use X-Tenant header, JWT claim, etc.
    tenant_id = subdomain  # or request.headers.get("X-Tenant")

    if not tenant_id or not re.match("^[a-z0-9_]+$", tenant_id):
        raise HTTPException(400, "Invalid tenant")

    schema_name = f"tenant_{tenant_id}"
    
    # Verify tenant exists
    from .database import SessionLocalBase
    with SessionLocalBase() as db:
        result = db.execute(text("SELECT 1 FROM public.tenants WHERE schema_name = :s"), {"s": schema_name}).fetchone()
        if not result:
            raise HTTPException(404, "Tenant not found")

    with tenant_context(schema_name):
        response = await call_next(request)
    return response
```

Add to your FastAPI app:

```python
app = FastAPI(dependencies=[Depends(get_db)])
app.middleware("http")(tenant_middleware)
```

#### 4. Your CRUD functions stay exactly the same!

All your existing `crud.py` functions work unchanged because they use the injected `db: Session` which now automatically points to the correct tenant schema.

#### 5. Global tables (optional)

Keep a few tables in `public` schema:
- `public.tenants`
- `public.users` (if you have cross-tenant admins)
- audit logs, billing, etc.

#### Benefits you get with this architecture

- 100% data isolation (no accidental leaks via tenant_id filters)
- Easy GDPR deletion: `DROP SCHEMA tenant_123 CASCADE;`
- Individual tenant backups/restores
- Can move big tenants to separate DB later if needed
- Still excellent performance (connection pooling per schema)
- Works perfectly with your existing Alembic migrations (just add schema support)

#### Tools that help

- alembic-utils or alembic-schema for schema-aware migrations
- Flask-Migrate/alembic with `-x schema=...`
- pg_dump -n tenant_123 for per-tenant backups

This pattern is used successfully by companies like Citus Data (before Microsoft), Hasura, and many SaaS platforms with thousands of tenants.

Let me know if you want the Row-Level Security (RLS) version instead (shared schema + PostgreSQL policies) — it's simpler but has slightly higher risk of leaks if policies are misconfigured. For 100+ tenants with compliance needs, schema-based is safer and cleaner.