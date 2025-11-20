# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Table
from sqlalchemy.sql import func
from .base import Base  # ← NOW FROM BASE.PY


# Many-to-many connection table for the ownership graph
entity_connections = Table(
    "entity_connections",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("from_type", String(20), nullable=False),        # 'legal' or 'natural'
    Column("from_id", Integer, nullable=False),
    Column("to_type", String(20), nullable=False),
    Column("to_id", Integer, nullable=False),
    Column("relation", String(50), nullable=False),
    Column("share_percentage", String(20), nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)


class LegalPerson(Base):
    __tablename__ = "legal_persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    registration_number = Column(String, unique=True, nullable=False)
    jurisdiction = Column(String)
    incorporation_date = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NaturalPerson(Base):
    __tablename__ = "natural_persons"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    nationality = Column(String)
    date_of_birth = Column(String)
    tax_id = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())