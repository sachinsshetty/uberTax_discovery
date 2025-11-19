from sqlalchemy import Column, String, Date, JSON
from sqlalchemy.orm import declarative_base
from .base import BaseModel

Base = declarative_base()

class LegalPerson(Base, BaseModel):
    __tablename__ = "legal_persons"

    registration_no = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    jurisdiction = Column(String, nullable=False)
    incorporation_date = Column(Date)
    status = Column(String, default="ACTIVE")
    metadata = Column(JSON, default=dict)