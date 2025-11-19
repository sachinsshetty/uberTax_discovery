from sqlalchemy import Column, String, Date, JSON
from sqlalchemy.orm import declarative_base
from .base import BaseModel

Base = declarative_base()
class NaturalPerson(Base, BaseModel):
    __tablename__ = "natural_persons"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date)
    nationality = Column(String)
    metadata = Column(JSON, default=dict)