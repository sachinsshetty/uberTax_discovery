# app/dependencies.py
from contextlib import contextmanager
from typing import Generator
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .database import get_db as get_tenant_db_session, _current_tenant

# ----------------------------------------------------------------------
# 1. Low-level context manager - uses the tenant-aware session from database.py
# ----------------------------------------------------------------------
@contextmanager
def _tenant_db_session():
    """
    Internal context manager that yields a tenant-scoped Session.
    It automatically commits on success, rolls back on exceptions,
    and always closes the session.
    """
    tenant = _current_tenant.get()
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tenant context. Request did not pass through tenant middleware."
        )

    db: Session = None
    try:
        # This generator comes from database.py (tenant-specific engine)
        gen = get_tenant_db_session()
        db = next(gen)
        yield db
        db.commit()                    # <-- Critical: commit only if no exception
    except SQLAlchemyError as exc:
        if db:
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        ) from exc
    except Exception:
        if db:
            db.rollback()
        raise
    finally:
        if db and db.is_active:
            db.close()


# ----------------------------------------------------------------------
# 2. Public dependency - exactly what your routers already use
# ----------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """
    Dependency used in route signatures:
        db: Session = Depends(get_db)
    Fully backward compatible, now tenant-aware and safe.
    """
    with _tenant_db_session() as db:
        yield db


# ----------------------------------------------------------------------
# 3. Optional: Helper to get current tenant in routes (useful for logging/auditing)
# ----------------------------------------------------------------------
def get_current_tenant() -> str:
    tenant = _current_tenant.get()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context missing"
        )
    return tenant


# ----------------------------------------------------------------------
# 4. Optional: Request-scoped helper if you want tenant from request state
# ----------------------------------------------------------------------
def get_current_tenant_from_request(request: Request) -> str:
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant not set")
    return tenant