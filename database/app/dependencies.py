# app/dependencies.py
from typing import Generator
from sqlalchemy.orm import Session
from .database import SessionLocal
from fastapi import Depends, HTTPException, status
from contextlib import contextmanager

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()                # <-- THIS WAS MISSING
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Keep the old name for backward compatibility with all routers
def get_db() -> Generator[Session, None, None]:
    with get_db_session() as db:
        yield db