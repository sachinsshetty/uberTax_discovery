# File: schemas.py (updated)
from pydantic import BaseModel, Field
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
    clientId: str = Field(..., alias="client_id")
    companyName: str = Field(..., alias="company_name")
    country: str = Field(..., alias="country")
    newRegulation: str = Field(..., alias="new_regulation")
    deadline: Optional[date] = Field(None, alias="deadline")  # Changed to date; auto-serializes to ISO str in JSON
    status: str = Field(..., alias="status")

    class Config:
        from_attributes = True  # Allows mapping from SQLAlchemy models