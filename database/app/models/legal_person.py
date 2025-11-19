from sqlalchemy import Column, String, Date, JSON, DateTime, func, Uuid
import uuid
from .base import Base

class LegalPerson(Base):
    __tablename__ = "legal_person"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    registration_no = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    jurisdiction = Column(String)
    incorporation_date = Column(Date)
    status = Column(String, default="ACTIVE")
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())