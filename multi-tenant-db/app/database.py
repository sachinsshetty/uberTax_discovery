# app/database.py
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

# ContextVar to track current tenant schema in async/Thread-local context
_current_tenant: ContextVar[str | None] = ContextVar("current_tenant", default=None)

# Base engine — always connected to the single database (used for public schema & tenant management)
base_engine = create_engine(
    settings.DATABASE_URL,
    isolation_level="AUTOCOMMIT",
    pool_pre_ping=True
)
SessionLocalBase = sessionmaker(bind=base_engine)

# Cache for tenant-specific engines (one per schema)
_engines_cache: dict[str, any] = {}
_engines_lock = threading.Lock()


def get_tenant_engine(tenant_schema: str):
    """
    Return a SQLAlchemy engine bound to the same database,
    but with search_path set to the tenant's schema (and public fallback).
    """
    if tenant_schema in _engines_cache:
        return _engines_cache[tenant_schema]

    with _engines_lock:
        if tenant_schema not in _engines_cache:
            engine = create_engine(
                settings.DATABASE_URL,  # ← Same DB, do NOT append schema name!
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_timeout=30,
                connect_args={
                    # This is the correct way: only change search_path
                    "options": f"-csearch_path={tenant_schema},public"
                },
            )
            _engines_cache[tenant_schema] = engine

    return _engines_cache[tenant_schema]


def get_db() -> Generator[Session, None, None]:
    """
    Dependency used in routers: db: Session = Depends(get_db)
    Returns a session scoped to the current tenant schema.
    """
    tenant_schema = _current_tenant.get()
    if not tenant_schema:
        raise ValueError("No tenant context set. Use tenant_context() manager.")

    engine = get_tenant_engine(tenant_schema)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Context manager to temporarily set the active tenant schema
from contextlib import contextmanager


@contextmanager
def tenant_context(schema: str):
    """
    Used in middleware to set the current tenant for the duration of the request.
    """
    token = _current_tenant.set(schema)
    try:
        yield
    finally:
        _current_tenant.reset(token)