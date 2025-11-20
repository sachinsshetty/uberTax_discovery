# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings
from typing import Generator
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/registry"

    model_config = {
        "env_file": ".env",        # loads .env if present
        "env_file_encoding": "utf-8",
    }

# Instantiate settings (loads from env or .env file)
settings = Settings()

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,           # recommended for production
    pool_size=10,
    max_overflow=20,
    echo=False,                   # set True only for debugging
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Correct way in SQLAlchemy 2.0+
Base = declarative_base()


# Dependency for FastAPI routes
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()