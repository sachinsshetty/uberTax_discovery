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