# models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Table, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# =============================================================================
# GRAPH: entity_connections – ONLY THIS TABLE IS FIXED (performance + safety)
# =============================================================================
entity_connections = Table(
    "entity_connections",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("from_type", String(20), nullable=False, index=True),
    Column("from_id", Integer, nullable=False, index=True),
    Column("to_type", String(20), nullable=False, index=True),
    Column("to_id", Integer, nullable=False, index=True),
    Column("relation", String(50), nullable=False),
    Column("share_percentage", Float, nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),

    # FIXED: Prevent duplicate connections
    UniqueConstraint("from_type", "from_id", "to_type", "to_id", "relation", name="uniq_connection"),
    # Indexes created in DB migration below (not inline to avoid re-creation issues)
)

# =============================================================================
# YOUR ORIGINAL LEGAL & NATURAL PERSONS – 100% UNCHANGED
# =============================================================================
class LegalPerson(Base):
    __tablename__ = "legal_persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    registration_number = Column(String, unique=True, nullable=False, index=True)
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
    tax_id = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())