# File: schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class ClientProfileCreate(BaseModel):
    client_id: str
    company_name: str
    country: str
    new_regulation: str
    deadline: Optional[str] = None  # ISO format string
    status: str = "pending"

class ClientProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    country: Optional[str] = None
    new_regulation: Optional[str] = None
    deadline: Optional[str] = None  # ISO format string
    status: Optional[str] = None

class ClientProfileResponse(BaseModel):
    clientId: str
    companyName: str
    country: str
    newRegulation: str
    deadline: Optional[str] = None  # ISO format string
    status: str

    class Config:
        from_attributes = True  # Allows mapping from SQLAlchemy models